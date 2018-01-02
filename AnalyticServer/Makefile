#### Compiler and tool definitions shared by all build targets #####
CCC = g++
CXX = g++
BASICOPTS = -g -m64 -std=gnu++11
CCFLAGS = $(BASICOPTS)
CXXFLAGS = $(BASICOPTS)
CCADMIN = 


# Define the target directories.
TARGETDIR_AnalyticsServer = Executables


all: $(TARGETDIR_AnalyticsServer)/AnalyticsServer

OBJS_AnalyticsServer =  \
	$(TARGETDIR_AnalyticsServer)/AnalyticsServer.o \
	$(TARGETDIR_AnalyticsServer)/Datahandler.o \
	$(TARGETDIR_AnalyticsServer)/Server.o \
	$(TARGETDIR_AnalyticsServer)/mServer.o \
	$(TARGETDIR_AnalyticsServer)/aServer.o \
	$(TARGETDIR_AnalyticsServer)/AppPool.o \
	$(TARGETDIR_AnalyticsServer)/Engine.o \
	$(TARGETDIR_AnalyticsServer)/pEngine.o \
	$(TARGETDIR_AnalyticsServer)/rEngine.o \
	$(TARGETDIR_AnalyticsServer)/Rconnection.o \
	$(TARGETDIR_AnalyticsServer)/httpMessage.o\
	$(TARGETDIR_AnalyticsServer)/httpRequest.o\
	$(TARGETDIR_AnalyticsServer)/httpResponse.o\
	$(TARGETDIR_AnalyticsServer)/ServiceDefinition.o
#SYSLIBS_AnalyticsServer = -L/usr/X11R6/lib -lm -lcrypt -pthread -lpthread -ldl -lconfig++ -lpython2.7 -lboost_system -lboost_filesystem
SYSLIBS_AnalyticsServer = -lcrypt -pthread -lconfig++ -lpython2.7 -lboost_system -lboost_filesystem
#-lutil -lm  -Xlinker -export-dynamic -Wl,-O1 -Wl,-Bsymbolic-functions
#SYSLIBS_AnalyticsServer = -L/usr/lib/python3.5/config-3.5m-x86_64-linux-gnu -L/usr/lib -lpython3.5m -ldl -lcrypt -pthread -lpthread -lconfig++ -lboost_system -lboost_filesystem
USERLIBS_AnalyticsServer = $(SYSLIBS_AnalyticsServer) 
LDLIBS_AnalyticsServer = $(USERLIBS_AnalyticsServer)

# Link or archive
$(TARGETDIR_AnalyticsServer)/AnalyticsServer: $(TARGETDIR_AnalyticsServer) $(OBJS_AnalyticsServer) $(DEPLIBS_AnalyticsServer)
	$(LINK.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ $(OBJS_AnalyticsServer) $(LDLIBS_AnalyticsServer)

# Compile source files into .o files
$(TARGETDIR_AnalyticsServer)/AnalyticsServer.o: $(TARGETDIR_AnalyticsServer) AnalyticsServer.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ AnalyticsServer.cpp
	
$(TARGETDIR_AnalyticsServer)/Datahandler.o: $(TARGETDIR_AnalyticsServer) Datahandler.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ Datahandler.cpp
	
$(TARGETDIR_AnalyticsServer)/Server.o: $(TARGETDIR_AnalyticsServer) Server.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ Server.cpp
	
$(TARGETDIR_AnalyticsServer)/mServer.o: $(TARGETDIR_AnalyticsServer) mServer.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ mServer.cpp

$(TARGETDIR_AnalyticsServer)/aServer.o: $(TARGETDIR_AnalyticsServer) aServer.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ aServer.cpp

$(TARGETDIR_AnalyticsServer)/ServiceDefinition.o: $(TARGETDIR_AnalyticsServer) ServiceDefinition.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ ServiceDefinition.cpp

$(TARGETDIR_AnalyticsServer)/AppPool.o: $(TARGETDIR_AnalyticsServer) AppPool.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ AppPool.cpp	
	
$(TARGETDIR_AnalyticsServer)/Engine.o: $(TARGETDIR_AnalyticsServer) Engine.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ Engine.cpp
	
$(TARGETDIR_AnalyticsServer)/pEngine.o: $(TARGETDIR_AnalyticsServer) pEngine.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ pEngine.cpp

$(TARGETDIR_AnalyticsServer)/rEngine.o: $(TARGETDIR_AnalyticsServer) rEngine.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ rEngine.cpp

$(TARGETDIR_AnalyticsServer)/Rconnection.o: $(TARGETDIR_AnalyticsServer) Rconnection.cc
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ Rconnection.cc

$(TARGETDIR_AnalyticsServer)/httpMessage.o: $(TARGETDIR_AnalyticsServer) httpMessage.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ httpMessage.cpp

$(TARGETDIR_AnalyticsServer)/httpRequest.o: $(TARGETDIR_AnalyticsServer) httpRequest.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ httpRequest.cpp

$(TARGETDIR_AnalyticsServer)/httpResponse.o: $(TARGETDIR_AnalyticsServer) httpResponse.cpp
	$(COMPILE.cc) $(CCFLAGS_AnalyticsServer) $(CPPFLAGS_AnalyticsServer) -o $@ httpResponse.cpp
	
	

#### Clean target deletes all generated files ####
clean:
	rm -f \
		$(TARGETDIR_AnalyticsServer)/AnalyticsServer \
		$(TARGETDIR_AnalyticsServer)/AnalyticsServer.o \
		$(TARGETDIR_AnalyticsServer)/Datahandler.o \
		$(TARGETDIR_AnalyticsServer)/Server.o \
		$(TARGETDIR_AnalyticsServer)/aServer.o \
		$(TARGETDIR_AnalyticsServer)/mServer.o \
		$(TARGETDIR_AnalyticsServer)/ServiceDefinition.o \
		$(TARGETDIR_AnalyticsServer)/AppPool.o \
		$(TARGETDIR_AnalyticsServer)/Engine.o \
		$(TARGETDIR_AnalyticsServer)/pEngine.o \
		$(TARGETDIR_AnalyticsServer)/rEngine.o \
		$(TARGETDIR_AnalyticsServer)/Rconnection.o \
		$(TARGETDIR_AnalyticsServer)/httpMessage.o \
		$(TARGETDIR_AnalyticsServer)/httpRequest.o \
		$(TARGETDIR_AnalyticsServer)/httpResponse.o
	$(CCADMIN)
	rm -f -r $(TARGETDIR_AnalyticsServer)


# Create the target directory (if needed)
$(TARGETDIR_AnalyticsServer):
	mkdir -p $(TARGETDIR_AnalyticsServer)

# Enable dependency checking
.KEEP_STATE:
.KEEP_STATE_FILE:.make.state.GNU-amd64-Linux