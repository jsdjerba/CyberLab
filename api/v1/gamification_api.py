from flask import Blueprint, request, g
from domain.exceptions import ValidationError # Import correct depuis le Domaine
from api.middleware.response_builder import ResponseBuilder
from api.middleware.auth_guard import require_auth
from api.mappers.gamification_mapper import GamificationMapper

def create_gamification_api(gamification_service):
    bp = Blueprint("gamification", __name__, url_prefix="/api/v1/gamification")

    @bp.route("/profile", methods=["GET"])
    @require_auth
    def get_profile():
        student_id = g.user.get("student_id")
        profile_dto = gamification_service.get_profile(student_id)
        return ResponseBuilder.success(GamificationMapper.to_profile_dict(profile_dto))

    @bp.route("/badges", methods=["GET"])
    @require_auth
    def get_badges():
        student_id = g.user.get("student_id")
        badges = gamification_service.get_badges(student_id)
        return ResponseBuilder.success(GamificationMapper.to_badges_list(badges))

    @bp.route("/leaderboard", methods=["GET"])
    @require_auth
    def get_leaderboard():
        limit = int(request.args.get("limit", 10))
        if limit <= 0 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100.")
        entries = gamification_service.get_leaderboard(limit)
        return ResponseBuilder.success(GamificationMapper.to_leaderboard_list(entries))

    return bp