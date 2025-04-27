"""
Contains the pydantic models for validating Spamhaus API responses.
""" 
import re
from datetime import datetime

from pydantic import BaseModel, Field

class DROPEntry(BaseModel):
    """Single entry in the DROP list."""
    asn: int | None = None
    rir: str | None = None
    domain: str 
    cc: str | None = None
    asname: str | None = None
    
    @property
    def valid_domain(self) -> bool:
        """
        Check if the domain has a TLD:
        """
        ptrn = re.compile(r"^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
        return bool(ptrn.match(self.domain))
    
    @property
    def pihole_regex(self) -> str:
        """
        Returns a pihole regex'd version of the domain
        
        example input: "ncryptd.net"
        example output: "(\.|^)ncryptd\.net$"
        
        example input: "a.regular.domain.cn"
        example output: "(\.|^)a\.regular\.domain\.cn$"
        """
        return r"(\.|^)" + self.domain.replace(".", r"\.") + r"$"
    
class PiHoleGroup(BaseModel):
    """Pi-hole group model."""
    name: str
    comment: str | None = None
    enabled: bool
    id: int
    date_added: datetime = Field(default_factory=datetime.fromtimestamp)
    date_modified: datetime = Field(default_factory=datetime.fromtimestamp)
    
class PiHoleGroupList(BaseModel):
    """Pi-hole group list model."""
    groups: list[PiHoleGroup]
    
    @property
    def enabled_groups(self) -> list[PiHoleGroup]:
        """
        Returns a list of enabled groups.
        """
        return [group for group in self.groups if group.enabled]
    
class PiHoleDomain(BaseModel):
    """Pi-hole domain model."""
    domain: str
    unicode: str | None = None
    domainType: str | None = Field(alias="type", default=None)
    kind: str | None = None
    comment: str | None = None
    groups: list[int] | None = None
    enabled: bool | None = None
    ID: int | None = Field(alias="id", default=None)
    date_added: datetime | None = Field(alias="date_added", default_factory=datetime.fromtimestamp)
    date_modified: datetime | None = Field(alias="date_modified", default_factory=datetime.fromtimestamp)

    
class PiHoleDomainList(BaseModel):
    """Pi-hole domain list model."""
    domains: list[PiHoleDomain]
    
    @property
    def enabled_domains(self) -> list[PiHoleDomain]:
        """
        Returns a list of enabled domains.
        """
        return [domain for domain in self.domains if domain.enabled]