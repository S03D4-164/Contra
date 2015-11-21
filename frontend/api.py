class ContraAPI(object):
    def __init__(self):
        self.url = "http://localhost:8000/api/"
        self.dns = self.url + "dns_resolve"
        self.whois_domain = self.url + "whois_domain"
        self.whois_ip = self.url + "whois_ip"
        self.local_ghost = self.url + "local/ghost/"
        self.local_thug = self.url + "local/thug/"
        self.docker_ghost = self.url + "docker/ghost/"
        self.docker_thug = self.url + "docker/thug/"
