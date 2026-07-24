class GradingPolicy:
    def calculate_xp(self, base_points: int, attempts: int) -> int:
        if base_points <= 0:
            return 0
        if attempts <= 1:
            return base_points
        elif attempts == 2:
            return int(base_points * 0.75)
        else:
            return int(base_points * 0.50)