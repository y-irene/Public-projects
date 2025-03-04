#include <queue.h>
#include "skel.h"

// Routing table implementation
struct rTable_entry {
	uint32_t prefix;
	uint32_t mask;
	uint32_t nextHop;
	int interface;
};

// Unsigned int value of string IP address
uint32_t ipToInt (char *ipAddr) {
	struct in_addr ip;
    inet_aton(ipAddr, &ip);
    return htonl(ip.s_addr);
};

// Compare function for routing table entries
int cmpEntries (const void *a, const void *b) {
	struct rTable_entry *e1 = (struct rTable_entry *)a;
	struct rTable_entry *e2 = (struct rTable_entry *)b;
	if (e1->prefix != e2->prefix)
		return e1->prefix - e2->prefix;
	else
		return e2->mask - e1->mask;
}

// Function that parses routing table from file
int parseRTable (char *fName, struct rTable_entry **rTable) {
	// Open routing table file to read entries
	FILE *fp = fopen(fName, "r");
	// Check if file has been opened correctly
	if (fp == NULL) {
		perror("Cannot open file");
		exit(-1);
	}

	// Add all entries of routing table in a queue
	queue tableQ = queue_create();
	char prefix[16], mask[16], next_hop[16];
	int interface;
	int len = 0;
	while(fscanf(fp, "%s %s %s %d\n", prefix, next_hop, mask, &interface) == 4){
		struct rTable_entry *entry = malloc(sizeof(struct rTable_entry));
		entry->prefix = ipToInt(prefix);
		entry->mask = ipToInt(mask);
		entry->nextHop = ipToInt(next_hop);
		entry->interface = interface;
		queue_enq(tableQ, entry);
		len++;
	}

	// Convert queue to vector
	*rTable = calloc(len, sizeof(struct rTable_entry));
	for (int i = 0; i < len; i++){
		(*rTable)[i] = *(struct rTable_entry *)queue_deq(tableQ);
	}
	free(tableQ);

	// Sort routing table by prefix and mask
	qsort(*rTable, len, sizeof(struct rTable_entry), cmpEntries);

	return len;
}

// Search the entry for an IP 
// Binary search for last match occurence - it has the longest mask
struct rTable_entry* search(uint32_t ip, struct rTable_entry *rTable, int len){
	struct rTable_entry *entry = NULL;

	int left = 0, right = len - 1;
	int mid , res = -1;

	while(left <= right) {
		mid = left + ((right - left) / 2);
		if (rTable[mid].prefix <= (ip & rTable[mid].mask)) {
			res = mid;
			left = mid + 1;
		} else {
			right = mid - 1;
		}
	}

	if ((res != -1) && (rTable[res].prefix == (ip & rTable[res].mask)))
		entry = &rTable[res];
	return entry;
}


// ARP table implementation
struct arp_entry {
	uint32_t ip;
	uint8_t mac[6];
};

// Search an IP in an ARP table
// If not found, return NULL
uint8_t* get_mac (uint32_t ip, struct arp_entry *arpTable, int arpT_len){
	for (int i = 0; i < arpT_len; i++) {
		if (ip == arpTable[i].ip)
			return arpTable[i].mac;
	}
	return NULL;
}

int add_entry (struct arp_entry **arpTable, int *arpT_len, uint32_t ip,
			   uint8_t mac[6]) {
	// If entry already exists, don't add it again
	if(get_mac(ip, *arpTable, *arpT_len) != NULL)
		return 1;
	
	// Add new entry in ARP table
	struct arp_entry *new_table = realloc(*arpTable, (*arpT_len + 1) * 
		(sizeof(struct arp_entry)));
	new_table[*arpT_len].ip = ip;
	memcpy(new_table[*arpT_len].mac, mac, 6);
	*arpT_len = *arpT_len + 1;
	*arpTable = new_table;
	return 0;
}

// Auxiliary functions

// Create a vector with IPs of all interfaces
uint32_t* get_my_ips (int n){
	uint32_t *myIPs = calloc(n, sizeof(uint32_t));
	for (int i = 0; i < n; i++)
		myIPs[i] = ipToInt(get_interface_ip(i));

	return myIPs;
}

// Check if an IP is one of router's IPs
int ip_is_mine(uint32_t *myIPs, int n, uint32_t dest) {
	for (int i = 0; i < n; i++) {
		if (!(myIPs[i] ^ dest)){
			return i;
		}
	}
	return -1;
}

int main(int argc, char *argv[])
{
	packet m;
	int rc;
	int numInterfaces = argc - 2;
	init(numInterfaces, argv + 2);

	// Get all of router's IPs
	uint32_t *myIPs = get_my_ips(numInterfaces);

	// Initialize routing table
	struct rTable_entry *rTable = NULL;
	int rTable_len = parseRTable(argv[1], &rTable);

	// Initialize ARP table
	struct arp_entry *arpTable = NULL;
	int arpTable_len = 0;

	// Initialize packets queue
	queue pkq = queue_create();

	while (1) {
		rc = get_packet(&m);
		DIE(rc < 0, "get_message");

		// Extract all types of headers
		struct ether_header *eth_hdr = (struct ether_header *)(m.payload);
		struct iphdr *ip_hdr = (struct iphdr *)(m.payload + 
								sizeof(struct ether_header));
		struct icmphdr *icmp_hdr = parse_icmp(m.payload);
		struct arp_header *arp_hdr = parse_arp(m.payload);

		// Check if packet is for current router
		int forME = ip_is_mine(myIPs, numInterfaces, ntohl(ip_hdr->daddr));
		if (forME != -1) {
			// Check if message is an ICMP ECHO equest
			if (icmp_hdr != NULL) {
				if(icmp_hdr->type == 8 && icmp_hdr->code == 0) {
					// Send ICMP ECHO reply
					uint8_t *sha = calloc(6,1);
					get_interface_mac(forME, sha);
					uint8_t *dha = calloc(6,1);
					memcpy(dha, eth_hdr->ether_shost, 6);
					send_icmp(ip_hdr->saddr, ip_hdr->daddr, sha, dha, 0, 0, 
						forME, icmp_hdr->un.echo.id, icmp_hdr->un.echo.sequence);
					
					free(sha);
					free(dha);
					continue;
				}
			}
		}
		
		// Check if packet is ARP
		if (arp_hdr != NULL) {
			int interface = ip_is_mine(myIPs, numInterfaces, 
									   ntohl(arp_hdr->tpa));
			
			if(ntohs(arp_hdr->op) == 1 && (interface != -1)) {
				// Received ARP request
				struct ether_header rether;
				get_interface_mac(interface, rether.ether_shost);
				memcpy(rether.ether_dhost, arp_hdr->sha, 6);
				rether.ether_type = htons(ETHERTYPE_ARP);
				// Send ARP reply
				send_arp(arp_hdr->spa, arp_hdr->tpa, &rether, interface, 
						 htons(2));
				continue;
			} else if (ntohs(arp_hdr->op) == 2) {
				// Received ARP reply
				// If it's not for me, drop packet
				if (interface == -1)
					continue;

				// Add entry to ARP table
				int exists = add_entry(&arpTable, &arpTable_len, 
					ntohl(arp_hdr->spa), arp_hdr->sha);
				// If entry already exists, no need to search queue for packets 
				// waiting to be sent
				if (exists == 1)
					continue;

				// Search queue for packets waiting to be sent to this MAC
				queue new = queue_create();
				packet *pk;
				while(!queue_empty(pkq)){
					// Extract packet from queue
					pk = (packet *)(queue_deq(pkq));
					eth_hdr = (struct ether_header *)(pk->payload);
					ip_hdr = (struct iphdr *)(pk->payload + 
											  sizeof(struct ether_header));
					struct rTable_entry *rentry = search(ntohl(ip_hdr->daddr), 
														 rTable, rTable_len);
					
					// If packet is waiting for another ARP reply, keep it in 
					// the queue
					if(rentry->nextHop != ntohl(arp_hdr->spa)) {
						queue_enq(new, &pk);
						continue;
					}

					// Otherwise, send packet
					memcpy(eth_hdr->ether_dhost, arp_hdr->sha, 6);
					send_packet(rentry->interface, pk);
				}

				// Update queue
				pkq = new;
				continue;
			}
		}
		
		// Check if packet TTL exceeded
		if (ip_hdr->ttl <= 1) {
			// If TTL exceeded, send ICMP error time exceeded
			uint8_t *sha = calloc(6,1);
			get_interface_mac(m.interface, sha);
			uint8_t *dha = calloc(6,1);
			memcpy(dha, eth_hdr->ether_shost, 6);
			send_icmp_error(ip_hdr->saddr, htonl(myIPs[m.interface]), sha, dha, 
							11, 0, m.interface);
			
			free(sha);
			free(dha);
			continue;
		}

		// Check packet checksum
		uint16_t oldCheck = ip_hdr->check;
		ip_hdr->check = 0;
		uint16_t checksum = ip_checksum(ip_hdr, sizeof(struct iphdr));
		// If checksum is wrong, drop packet
		if (checksum != oldCheck) {
			continue;
		}

		// Update packet TTL and checksum
		ip_hdr->ttl = ip_hdr->ttl - 1;
		ip_hdr->check = 0;
		ip_hdr->check = ip_checksum(ip_hdr, sizeof(struct iphdr));

		//Search routing table entry
		struct rTable_entry *rentry = search(ntohl(ip_hdr->daddr), rTable, 
											 rTable_len);
		if(rentry == NULL)
		{
			// If there is no entry for packet destination, send ICMP error 
			// destination unreachable
			uint8_t *sha = calloc(6,1);
			get_interface_mac(m.interface, sha);
			uint8_t *dha = calloc(6,1);
			memcpy(dha, eth_hdr->ether_shost, 6);
			send_icmp_error(ip_hdr->saddr, htonl(myIPs[m.interface]), sha, dha, 
							3, 0, m.interface);
			
			free(sha);
			free(dha);
			continue;
		}

		// Get next hop for packet
		uint32_t nextHop = rentry->nextHop;
		uint8_t *next_mac = get_mac(nextHop, arpTable, arpTable_len);

		// If the router doesn't know the MAC address for next hop, send ARP 
		// request on that interface
		if (next_mac == NULL) {
			// Create Ethernet header
			struct ether_header ether;
			hwaddr_aton("FF:FF:FF:FF:FF:FF", ether.ether_dhost);
			ether.ether_type = htons(ETHERTYPE_ARP);
			get_interface_mac(rentry->interface, ether.ether_shost);
			// Send ARP request
			send_arp(htonl(nextHop), htonl(myIPs[rentry->interface]), &ether, 
					 rentry->interface, htons(1));

			// Add packet to queue
			packet *to_send = malloc(sizeof(packet));
			memcpy(to_send, &m, sizeof(packet));
			queue_enq(pkq, to_send);
			continue;
		} else {
			// Package can be sent, so update Ethernet header and send it
			memcpy(eth_hdr->ether_dhost, next_mac, 6);
			send_packet(rentry->interface, &m);
		}
	}
}
