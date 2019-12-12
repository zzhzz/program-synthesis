
parser: y.tab.c y.tab.h lex.yy.c
	gcc -o parser y.tab.c lex.yy.c

y.tab.c y.tab.h: sygusparser.y
	bison -d -y sygusparser.y

lex.yy.c: sygusparser.l
	flex sygusparser.l

clean:
	rm -f parser y.tab.c y.tab.h lex.yy.c
