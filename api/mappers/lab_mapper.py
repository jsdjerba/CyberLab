from domain.dto.lab_response_dto import LabSummaryDTO, LabDetailDTO, LabProgressDTO, FlagSubmissionResultDTO

class LabMapper:
    @staticmethod
    def to_summary_list(dtos: list[LabSummaryDTO]) -> list[dict]:
        return [{"id": d.id, "title": d.title, "category": d.category, "difficulty": d.difficulty, "xp_reward": d.xp_reward} for d in dtos]

    @staticmethod
    def to_detail_dict(dto: LabDetailDTO) -> dict:
        return {"id": dto.id, "title": dto.title, "description": dto.description, "xp_reward": dto.xp_reward}

    @staticmethod
    def to_progress_dict(dto: LabProgressDTO) -> dict:
        return {"lab_id": dto.lab_id, "status": dto.status, "started_at": dto.started_at}

    @staticmethod
    def to_flag_result(dto: FlagSubmissionResultDTO) -> dict:
        return {"success": dto.success, "message": dto.message}