#include "ServiceDefinition.h"
#include "Datahandler.h"

int ServiceDefinition::readConfigFile(const std::string& configFilePath)
{    
    try {
        /* Read in information from the service configuration and place in
         * separate configuration setting objects.
         */
        Config serviceConfig;
        serviceConfig.readFile(configFilePath.c_str());
        Setting& root = serviceConfig.getRoot();
        
        FILE_LOG( logDEBUG4 ) << "Accessed Service Configuration, extracting info...";
        
        Setting& info = root["serviceInfo"];
        
        root.lookupValue("version", version);
        info.lookupValue("workingDirectory", workingDirectory);
        info.lookupValue("mainScript",mainScript);
        std::string languageIndicator;
        info.lookupValue("language",languageIndicator);
        if ( parseType( languageIndicator ) != serviceType::ERROR ){
            type = parseType( languageIndicator );
        }
        info.lookupValue("poolSize",poolSize);
        info.lookupValue("HTTP_Status", HTTP_Status);
        info.lookupValue("GET_HTML", GET_HTML);
        
        FILE_LOG( logDEBUG4 ) 
            << "Service Information: " << nli()
            << "Config Location: " << configFilePath << nli()
            << "Service version: " << version << nli()
            << "Working directory: " << workingDirectory << nli()
            << "Script name: " << mainScript << nli()
            << "Language Type: " << languageIndicator << nli()
            << "Pool size: " << poolSize << nli()
            << "HTTP Get Response Status: " << HTTP_Status << nli()
            << "URL Redirect location: " << GET_HTML;
        
        // Ensure the working directory is a valid one.
        if (ensureDirectory( workingDirectory ) != 0) return -4;
        
        if( HTTP_Status == 200 ){
            // Read in get page data.
            if ( readHTMLFile( GET_HTML ) != 0 ){return -5;}
        }
        else{
            // Record location.
            if ( GET_HTML.substr(0,7) != "http://" ){
                GET_HTML = "http://" + GET_HTML;
            }
        }
    } 
    catch(const FileIOException &fioex)
    {
        FILE_LOG(logDEBUG1) 
            << "IO Error attempting to access config file: " << configFilePath;
        return(-1);
    }
    catch(const ParseException &pex)
    {
        FILE_LOG(logDEBUG1) 
            << "ParseException raised - The service configuration file contains a "
            << pex.getError() << " on line " << pex.getLine();
        return(-2);
    }
    catch (const SettingNotFoundException &nfex)
    {
        FILE_LOG( logDEBUG1 ) << "Required service setting not found.";
        return(-3);
    }
    
    return 0;
}

ServiceDefinition::serviceType ServiceDefinition::parseType(std::string type){
    if( type == "PYTHON") return serviceType::PYTHON;
    else if ( type == "R") return serviceType::R;
    else return serviceType::ERROR;
}

int ServiceDefinition::ensureDirectory( std::string filePath ){
    
    std::string groupLoc = Datahandler::getServices()->root_directory;
    
    if( filePath[0] == '.') filePath = groupLoc + filePath.substr(2);
    workingDirectory = filePath;
    
    struct stat buffer; 
    if( stat( filePath.c_str(), &buffer ) == 0 ) return 0;
    else {
        FILE_LOG( logDEBUG1 ) << "Error on ensuring working directory of service";
        return -1;
    }
}

int ServiceDefinition::readHTMLFile( std::string filePath )
{
    std::ifstream html_ifstream( filePath );
    if( html_ifstream.good() == 1 ){
        char fileLine[256];
        size_t i;
        std::string content;
        while( html_ifstream.good() ){
            html_ifstream.getline(fileLine, 256, '\n');
            i = ((std::string) fileLine).find_first_not_of( ' ' );
            if ( i == std::string::npos ) content = content + "";
            else content = content + ((std::string) fileLine).substr( i, ((std::string) fileLine).find_last_not_of(' ')-i+1 );
        }
        GET_HTML = content;
        return 0;
    } else {
        return -1;
    }
}