#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path
from urllib import request
from urllib.error import HTTPError
import os, subprocess, codecs, shutil, sys

#
#TODO: Massive clean-up. There's so much redundant shit here
#

CurrentPath = Path(os.path.dirname(os.path.abspath(__file__)))
BackupUpdatesUrl = "http://mtgarena.downloads.wizards.com/Alpha/Windows32/updates.txt"


class ANSIColors:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    end = '\033[0m'


class HTPPErrorHandler:
    def __init__(self, error: HTTPError) -> None:
        self.error = error

    def handle(self) -> None:
        print("{0}  Something went wrong wile downloading:\n\n{2}{1}"
              .format(ANSIColors.yellow, self.error, ANSIColors.end))
    

class LAUNCHER:
    def __init__(self) -> None:
        #Set the paths to the config and exe
        self.configFile = CurrentPath.joinpath("MTGAUpdater.ini")
        self.pythonConfigFile = CurrentPath.joinpath("PythonConfig.ini")
        self.updatedConfigFile = CurrentPath.joinpath("UpdatedConfig.ini")
        self.updaterModulePath = CurrentPath.joinpath("MTGAUpdater.exe")
        self.version = "0"
    
    @staticmethod
    def launchGameAndExit(prefix: str)-> None:
        bashCommand = "WINEPREFIX=\"" + str(prefix) + "\" wine \"" + str(CurrentPath.joinpath("MTGA.exe")) + "\""
        print("{0}Printing launching game output, if there are errors please make an issue:\n{1}{2}"
              .format(ANSIColors.yellow, subprocess.check_output(['bash','-c', bashCommand]), ANSIColors.end))
        #And lastly: Set the version.
        self.writeCurrentVersionToConfig()
        
        exit(0)
        
    @staticmethod
    def installAndEndItInPrefixWith(prefix: Path, argument: str):
        bashCommand = "WINEPREFIX=\"" + str(prefix) + "\" msiexec.exe " + argument
        print("{0}Printing 'msiexec'-file output, if there are errors please make an issue:\n{1}{2}"
              .format(ANSIColors.yellow, subprocess.check_output(['bash','-c', bashCommand]), ANSIColors.end))
        
        #And lastly: Set the version.
        self.writeCurrentVersionToConfig()
        
        exit(0)
        
    @staticmethod
    def checkProductCode(parser: ConfigParser, version: str):
        try:
            return parser['Latest'][version + 'ProductCode']
        except:
            return None
        
    @staticmethod
    def getProductCodeFromConfig(parser: ConfigParser) -> str:
        #Bunched this up to have the main() be more "clean"
        return LAUNCHER.checkProductCode(parser, ''), LAUNCHER.checkProductCode(parser, 'English'), \
               LAUNCHER.checkProductCode(parser, 'French'), LAUNCHER.checkProductCode(parser, 'Italian'), \
               LAUNCHER.checkProductCode(parser, 'German'), LAUNCHER.checkProductCode(parser, 'Spanish'), \
               LAUNCHER.checkProductCode(parser, 'Brazil')

    @staticmethod
    def regProductCodeIsSpecific(productCodes: []) -> bool:
        list = []
        list.extend(productCodes)
        #Remove base value (first return), since we're not here for that
        list[0] = None
        if list.count(None) == len(list):
            return False
        else:
            return True
        
    def writeCurrentVersionToConfig(self) -> None:
        config = ConfigParser()
        config.read(self.pythonConfigFile)
        config['launcher']['version'] = self.version

        with self.pythonConfigFile.open('w') as f:
            config.write(f)
        
        
    def getUpdateFile(self, url = BackupUpdatesUrl) -> str:
        try:
            with request.urlopen(url) as response:
                return response.read()
        except HTTPError as err:
            HTPPErrorHandler(err).handle()
            return None
        
    def makePythonConfigFile(self) -> None:
        config = ConfigParser()
        config['launcher'] = {}
        config['launcher']['version'] = self.version

        with self.pythonConfigFile.open('w') as f:
            config.write(f)
        
    def main(self) -> None:
        #Lets start with getting the WINEPREFIX...
        i = 0
        try:
            i = str(CurrentPath).index("drive_c")
        except ValueError:
            print("{0}{1}Couldn't get current WINEPREFIX\n\tEXITING...{2}"
                  .format(ANSIColors.bold, ANSIColors.red, ANSIColors.end))
            exit(1)
        #... From the current directory; up until the WINEPREFIX root
        prefix = Path(str(CurrentPath)[0:i])
        
        try:
            if not self.pythonConfigFile.exists():
                self.makePythonConfigFile()
            
            #Cache the first parser
            config = ConfigParser()
            config.read(self.configFile)
            
            #Check for some dumb shit as in the original
            url = config['General']['URL']
            if "Alpha" in url:
                url = url.replace("Alpha", "Live")
            elif "Stage" in url:
                url = url.replace(".downloads", ".int-downloads")
            
            
            if url is None:
                url = BackupUpdatesUrl
                
            with self.updatedConfigFile.open('wb') as file:
                file.write(self.getUpdateFile(url))
                
            updatedConfig = ConfigParser()
            updatedConfig.read(self.updatedConfigFile)
            #Since the `url` var has now had it's use lets re-use it.
            url = updatedConfig['Latest']['URL']
            #And get all the other shit needed to make this work.
            self.version = updatedConfig['Latest']['Version']
            
            #Get all the possible productcodes.
            productCode, enProductCode, frProductCode, itProductCode, deProductCode, \
                esProductCode, brProductCode = LAUNCHER.getProductCodeFromConfig(updatedConfig)
            
            pythonConfig = ConfigParser()
            pythonConfig.read(self.pythonConfigFile)
            
            if pythonConfig['launcher']['version'] is self.version:
                print("Already up to date:\n\tLaunching MTGA.exe...")
                LAUNCHER.launchGameAndExit(prefix);
            else:
                isEXE = ".exe" in url
                isMSI = ".msi" in url
                configAppName = config['General']['ApplicationName']
                
                #Specify where the file needs to go,
                #handy since we need to read it,
                #might as well contain it
                pythonLauncherRegKeysFile = CurrentPath.joinpath("pythonLauncherRegKeys.reg")
                regKeyLocation = "HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Wizards of the Coast\\"
                bashCommand = "WINEPREFIX=\"" + str(prefix) + "\" wine regedit /E " + "\"" + \
                              str(pythonLauncherRegKeysFile) + "\" " + \
                              "\"" + regKeyLocation + configAppName + "\""
                print("{0}Printing Registry file extraction output, if there are errors please make an issue:\n{1}{2}"
                      .format(ANSIColors.yellow, subprocess.check_output(['bash','-c', bashCommand]), ANSIColors.end))
                
                if not pythonLauncherRegKeysFile.exists():
                    print("bash command error: Couldn't extract registry file, are you sure MTGA is installed?\n\tPlease contact owner")
                    exit(1)
                

                regFile = ConfigParser(allow_no_value=True)       
                #Fuck you microsoft. Just export in UTF-8, is that so hard?
                with open(pythonLauncherRegKeysFile, 'r', encoding="utf-16le") as f:
                    regFile_string = '[dummy_section]\n\"' + f.read()
                regFile.read_string(regFile_string)
                
                #Everything aside from the "header" and section has extra quotes
                #And I don't trust it for shit, so catch this shit.
                #Get ProductLanguage and trim the quotes
                try:
                    regProductLanguage = regFile[(regKeyLocation + "MTGArena").replace('\\\\', '\\')]["\"ProductLanguage\""].replace('\"', '')
                except Exception as e:
                    print("{0}For some reason we couldn't get the registry entry for ProductLanguage,\n "
                          "open an issue and give as much\n info as possible @ \n "
                          "https://github.com/Farcrada/MTGALauncher.py/issues :\n{1}{2}"
                          .format(ANSIColors.yellow, e, ANSIColors.end))
                    regProductLanguage = None;
                #Get ProductCode and trim the quotes
                try:
                    regProductCode = regFile[(regKeyLocation + "MTGArena").replace('\\\\', '\\')]["\"ProductCode\""].replace('\"', '')
                except Exception as e:
                    print("{0}For some reason we couldn't get the registry entry for ProductCode,\n "
                          "open an issue and give as much\n info as possible @ \n "
                          "https://github.com/Farcrada/MTGALauncher.py/issues :\n{1}{2}"
                          .format(ANSIColors.yellow, e, ANSIColors.end))
                    regProductCode = None;
                
                #Reserve the argument variable
                argument = None
                
                if not isMSI:
                    if isEXE:
                        #Create temp dir for the inc downloads.
                        tempDir = CurrentPath.joinpath("mtga_launcher_temp")
                        mtgaInstaller = "MTGAInstaller.exe"
                        
                        download = self.getUpdateFile(url)
                        if download is None:
                            print("No update/download link:\n\tLaunching MTGA.exe...")
                            LAUNCHER.launchGameAndExit(prefix);
                        
                        if tempDir.exists():
                            shutil.rmtree(tempDir)
                        os.mkdir(tempDir)
                        
                        mtgaInstallerExe = tempDir.joinpath(mtgaInstaller)
                        with mtgaInstallerExe.open('wb') as f:
                            f.write(download)
                        
                        if mtgaInstallerExe.exists():
                            argument = ("/exelang " + regProductLanguage + " /qr") \
                                       if regProductLanguage else "/qr"
                            bashCommand = "WINEPREFIX=\"" + str(prefix) + "\" wine \"" + \
                                           str(mtgaInstallerExe) + "\" " + argument
                            print("{0}Printing Installer file output, if there are errors please make an issue:\n{1}{2}"
                                  .format(ANSIColors.yellow, subprocess.check_output(['bash','-c', bashCommand]), ANSIColors.end))
                            exit(0)
                    #End of isEXE
                #End of isMSI
                elif regProductCode is None:
                    if regProductLanguage:
                        argument = ("/i " + url + " TRANSFORMS:" + regProductLanguage + " /qr") \
                                   if regProductLanguage is not "1033" else ("/i " + url + " /qr")
                        LAUNCHER.installAndEndItInPrefixWith(prefix, argument)
                    else:
                        argument = "/i " + url + " /qr"
                        LAUNCHER.installAndEndItInPrefixWith(prefix, argument)
                #End of `regProductCode is None`
                elif LAUNCHER.regProductCodeIsSpecific(LAUNCHER.getProductCodeFromConfig(updatedConfig)):
                    argument = ("/i " + url + " " + " TRANSFORMS:" + regProductLanguage + \
                                " /qr REINSTALLMODE=vomus REINSTALL=ALL") if regProductLanguage \
                                else ("/i " + url + " /qr REINSTALLMODE=vomus REINSTALL=ALL")
                    LAUNCHER.installAndEndItInPrefixWith(prefix, argument)
                else:
                    argument = ("/i " + url + " TRANSFORMS:" + regProductLanguage + " /qr") \
                               if regProductLanguage is not "1033" else ("/i " + url + " /qr")
                    LAUNCHER.installAndEndItInPrefixWith(prefix, argument)
            #And lastly: Set the version.
            self.writeCurrentVersionToConfig()
        except Exception as e:
            #e = sys.exc_info()[0]
            print("{0}{1}Something fucked up, open an issue and give as much\n " 
                  "info as possible @ https://github.com/Farcrada/MTGALauncher.py/issues :\n{2}{3}"
                  .format(ANSIColors.red, ANSIColors.bold, ANSIColors.end, e))
            LAUNCHER.launchGameAndExit(prefix);
            #And launch the game.
        print("All done! I think...\n\tLaunching MTGA.exe...")
        LAUNCHER.launchGameAndExit(prefix);

if __name__ == '__main__':
    launcher = LAUNCHER()
    launcher.main()
