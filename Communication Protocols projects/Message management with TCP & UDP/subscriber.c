#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/tcp.h>
#include "helpers.h"

// Function that prints a message from server
void print_udp_msg (struct udp_msg m) {
    if (m.data_type == 0) {
        printf("%s:%d - %s - INT - %s\n", 
        	m.ip, m.port_udp, m.topic, m.payload);
    } else if (m.data_type == 1) {
        printf("%s:%d - %s - SHORT_REAL - %s\n", 
        	m.ip, m.port_udp, m.topic, m.payload);
    } else if (m.data_type == 2) {
        printf("%s:%d - %s - FLOAT - %s\n", 
        	m.ip, m.port_udp, m.topic, m.payload);
    } else if (m.data_type == 3) {
        printf("%s:%d - %s - STRING - %s\n", 
        	m.ip, m.port_udp, m.topic, m.payload);
    }
}

int main(int argc, char *argv[]) {
	setvbuf(stdout, NULL, _IONBF, BUFSIZ);

	// Check number of arguments
	DIE(argc < 4, "Subscriber error: Too few arguments.");

	// Check id length
	DIE(strlen(argv[1]) > 10, "Subscriber error: ID too long");

	// Get server address information
	struct sockaddr_in server_addr;
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(atoi(argv[3]));
	inet_aton(argv[2], &server_addr.sin_addr);

	// Create TCP socket
	int sockfd = socket(AF_INET, SOCK_STREAM, 0);
	DIE(sockfd < 0, "Subscriber error: Socket");

	// Connect to server
	int rs = connect(sockfd, (struct sockaddr *)(&server_addr), 
					sizeof(struct sockaddr));
	DIE(rs < 0, "Subscriber error: Connect");

	// Disable Neagle's algorithm
    int enable = 1;
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &enable, sizeof(int)) == -1) {
    perror("setsocketopt");
    exit(1);
    }

	// Create a subscriber message (type = 0 -> id message) to send id to server
	struct subscriber_msg *msg = calloc(1, sizeof(struct subscriber_msg));
	DIE(msg == NULL, "Subscriber error: Alloc failed");
	msg->type = 0;
	msg->sf = -1;
	memset(msg->payload, 0, 51);
	strcpy(msg->payload, argv[1]);

	// Send message to server
	int n = send(sockfd, msg, sizeof(struct subscriber_msg), 0);
	DIE(n < 0, "Subscriber error: ID message");

	// Create sockfd set
	fd_set read_set, tmp_set;
	FD_ZERO(&read_set);
	FD_ZERO(&tmp_set);
	FD_SET(STDIN_FILENO, &read_set);
	FD_SET(sockfd, &read_set);
	int fd_max = (STDIN_FILENO > sockfd) ? STDIN_FILENO : sockfd;

	// Buffer for messages received from server (udp messages)
	int len = sizeof(struct udp_msg);
	char buffer[len];

	while (1) {
		tmp_set = read_set;
		select(fd_max + 1, &tmp_set, NULL, NULL, NULL);

		if (FD_ISSET(STDIN_FILENO, &tmp_set)) {
			// If STDIN socket is set, read input
			memset(buffer, 0, len);
			fgets(buffer, len - 1, stdin);

			if (strncmp(buffer, "exit", 4) == 0){
				// If input command is exit, stop the client
				free(msg);
				break;
			} else {
				char *tok = strtok(buffer, " \n");
				if (strncmp(tok, "subscribe", 9) == 0) {
					// If input command is subscribe, get topic and sf
					tok = strtok(NULL, " \n");
					char topic[51];
					// Check if command is valid
					if (tok == NULL) {
						fprintf(stderr, "Subscriber error: Invalid command.\nSubscribe command should have the following format \"subscribe [topic] [sf = 0/1]\"\n");
						continue;
					}

					memset(topic, 0, 51);
					strcpy(topic, tok);

					tok = strtok(NULL, " \n");
					// Check if command is valid
					if (tok == NULL) {
						fprintf(stderr, "Subscriber error: Invalid command.\nSubscribe command should have the following format \"subscribe [topic] [sf = 0/1]\"\n");
						continue;
					}

					int sf = atoi(tok);
					if (sf != 0 && sf != 1) {
						fprintf(stderr, "Subscriber error: Invalid command.\nSubscribe command should have sf 0 or 1.\n");
						continue;
					}

					// Create subscribe message (type = 1)
					memset(msg, 0, sizeof(struct subscriber_msg));
					msg->type = 1;
					msg->sf = sf;
					strcpy(msg->payload, topic);

					// Send message to server and print message
					n = send(sockfd, msg, sizeof(struct subscriber_msg), 0);
					DIE(n < 0, "Subscriber error: Subscribe message");
					printf("Subscribed to topic.\n");
				} else if (strncmp(tok, "unsubscribe", 11) == 0) {
					// If input command is unsubscribe, get topic
					tok = strtok(NULL, " \n");
					// Check if command is valid
					if (tok == NULL) {
						fprintf(stderr, "Subscriber error: Invalid command.\nUnsubscribe command should have the following format \"unsubscribe [topic]\"\n");
						continue;
					}

					char topic[51];
					memset(topic, 0, 51);
					strcpy(topic, tok);

					// Create unsubscribe message (type = 2)
					memset(msg, 0, sizeof(struct subscriber_msg));
					msg->type = 2;
					memset(msg->payload, 0, 51);
					strcat(msg->payload, topic);

					// Send message to server and print message
					n = send(sockfd, msg, sizeof(struct subscriber_msg), 0);
					DIE(n < 0, "Subscriber error: Unsubscribe message");
					printf("Unsubscribed from topic.\n");
				} else {
					fprintf(stderr, "Subscriber error: Command not found.\nCommand should be one of the following:\n    -\"exit\",\n    -\"subscribe [topic] [sf = 0/1]\"\n    -\"unsubscribe [topic]\"\n");
				}
			}

		} else if (FD_ISSET(sockfd, &tmp_set)) {
			// If TCP socket is set, read first byte of message from server
			memset(buffer, 0, len);
			n = recv(sockfd, buffer, 1, 0);
			DIE(n < 0, "Subscribe error: Receive");

			if (n == 0) {
				// If server stopped, stop the subscriber
				break;
			} else {
				// If new message from UDP subscription, read the rest of the 
				// message and print it
				for (int current_byte = 1; current_byte < len; current_byte++) {
					n = recv(sockfd, buffer + current_byte, 1, 0);
					DIE(n < 0, "Subscribe error: Receive");
				}

				struct udp_msg *update = (struct udp_msg *)buffer;
				print_udp_msg(*update);
			}
		}
	}

	close(sockfd);
	return 0;
}