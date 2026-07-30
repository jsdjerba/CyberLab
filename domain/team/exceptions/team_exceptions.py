class TeamDomainException(Exception): pass
class NegativeScoreException(TeamDomainException): pass
class InvalidPointsException(TeamDomainException): pass
class DuplicateTeamMemberException(TeamDomainException): pass
class TeamCapacityExceededException(TeamDomainException): pass
class CaptainAlreadyExistsException(TeamDomainException): pass
class MemberNotFoundException(TeamDomainException): pass