#ifndef _HELPERS_H
#define _HELPERS_H 1

#include <stdio.h>
#include <stdlib.h>

// Macro for error checking (from lab)
#define DIE(assertion, call_description)	\
	do {									\
		if (assertion) {					\
			fprintf(stderr, "(%s, %d): ",	\
					__FILE__, __LINE__);	\
			perror(call_description);		\
			exit(EXIT_FAILURE);				\
		}									\
	} while(0)

#endif

#define MAX_CLIENTS 100

// Structure of messages sent by a subscriber to the server
// type is 0 for message with subscriber id, 1 for subscribe request and 2
// for unsubscribe request
// sf is 0/1 for subscribe messages and -1 for id and unsubscribe messages
struct __attribute__((__packed__)) subscriber_msg {
	int type;			// message type
	int sf;				// store and forward for subscribe
	char payload[51];
};

// Structure of messages sent by server to subscriber from UDP client
struct __attribute__((__packed__)) udp_msg {
	char ip[16];				// UDP client IP
	unsigned int port_udp;		// UDP client port
	char topic[51];				// message topic
	unsigned char data_type;	// message data type
	char payload[1501];			// message value in string format
};

// Structure for subscription information
struct subscription {
	char topic[51];				// topic
	int sf;						// store and forward value for subscription
	int unsent_msg_num;			// number of unsent messages
	struct udp_msg *unsent_msg;	// array of unsent messages
};

// Structure for subscriber information
struct subscriber {
	char id[11];							// subscriber id
	int sockfd;							// subscriber sockfd
	int connected;						// subscriber status
	int subscriptions_num;				// number fo subscriptions
	struct subscription *subscriptions;	// array of subscriptions
};