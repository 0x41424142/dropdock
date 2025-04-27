"""
Main runner for the Pi-Hole data puller
"""

from os import getenv
from datetime import datetime
from argparse import ArgumentParser

from dotenv import load_dotenv

from .puller import pull_data
from .pihole import PiHole
from .logger import setup_logging

# Set up logging
logger = setup_logging()
logger.info("Starting dropdock")
load_dotenv()

def main():
    drop_list = pull_data()
    logger.info(f"Pulled {len(drop_list)} entries from Spamhaus DROP")
    drop_list = [entry for entry in drop_list if entry.valid_domain]
    logger.info(f"Filtered to {len(drop_list)} valid domains")

    p = PiHole(
        base_url=getenv("PIHOLE_URL") or "https://pi.hole/api",
        password=getenv("PIHOLE_PW")
    )

    # first get groups. we will use these to 
    # add the entries to all groups
    if grps:= getenv("PIHOLE_GROUPS"):
        grps = grps.split(",")
        groups = p.get_groups(group_name=grps)
    else:
        groups = p.get_groups()
        
    # now, pull any domains already in pihole that have the comment "_SHDROPLIST"
    domains_in_phiole = p.get_domains(filter_by="comment", filter_value="_SHDROPLIST")

    # if any domains in pihole are NOT in the new list
    # from Spamhaus, remove them:
    domains_to_delete = []
    for domain in domains_in_phiole:
        if domain.domain not in [entry.pihole_regex for entry in drop_list]:
            domains_to_delete.append(domain)
            
    logger.info(f"Deleting {len(domains_to_delete)} domains from Pi-Hole")
    for domain in domains_to_delete:
        p.make_call(f"/domains/{domain.domainType}/{domain.kind}/{domain.domain}", "DELETE")
        logger.info(f"Deleted stale {domain.domain} from Pi-Hole")
        
    # if any domains in the new list are NOT in pihole
    # add them to pihole:
    domains_to_add = []
    for entry in drop_list:
        if entry.pihole_regex not in [domain.domain for domain in domains_in_phiole]:
            domains_to_add.append(entry)

    if domains_to_add:
        p.make_call(
            "/domains/deny/regex",
            "POST",
            payload={
                "domain": [entry.pihole_regex for entry in domains_to_add],
                "comment": "_SHDROPLIST",
                "enabled": True,
                "groups": [group.id for group in groups.enabled_groups] if groups else [],
            }
        )
        logger.info(f"Added {len(domains_to_add)} domains to Pi-Hole groups: {', '.join([group.name for group in groups.enabled_groups])}")
    else:
        logger.info("No new domains to add to Pi-Hole")
    logger.info(f"Finished at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()