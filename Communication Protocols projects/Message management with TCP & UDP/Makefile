all: server subscriber

server: server.c
	gcc -Wall -g -o server server.c -lm

subscriber: subscriber.c
	gcc -Wall -g -o subscriber subscriber.c -lm

clean:
	rm -f server subscriber
