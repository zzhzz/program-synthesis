


parser: main.o sygusparser.y.o sygusparser.l.o sygusparser.y.hh
	g++ -Wall -Og -ggdb -o $@ $^

%.o : %.cc
	g++ -Wall -c -Og -ggdb -o $@ $(CFLAGS) $< 

main.o: sygusparser_lexer.hh sygusparser.y.hh


sygusparser.y.cc sygusparser.y.hh: sygusparser.y
	bison -osygusparser.y.cc -d sygusparser.y

sygusparser.l.cc: sygusparser.l
	flex -osygusparser.l.cc sygusparser.l

clean:
	rm -f parser sygusparser.y.cc sygusparser.l.cc sygusparser.y.hh stack.hh *.o
