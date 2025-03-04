client: client.c helpers.c buffer.c
	gcc -Wall -Wextra -o client client.c buffer.c helpers.c parson/parson.c

run: client
	./client

clean:
	rm client
