TARGET = main
source = demo

all: $(TARGET)

main: $(source).o CJsonObject.o cJSON.o
	g++ -o main $(source).o CJsonObject.o cJSON.o

$(source).o: CJsonObject.hpp cJSON.h
CJsonObject.o: CJsonObject.hpp
cJSON.o: cJSON.h

clean:
	rm -f *.o
	rm -f $(TARGET)
        
        
