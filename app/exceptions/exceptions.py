class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class OrganizationNotFound(AppException):
    def __init__(self, organization_id: int):
        super().__init__(f"Организация с ID {organization_id} не найдена", status_code=404)


class BuildingNotFound(AppException):
    def __init__(self, building_id: int):
        super().__init__(f"здание с ID {building_id} не найдено", status_code=404)


class ActivityNotFound(AppException):
    def __init__(self, product_id_or_url: str):
        super().__init__(f"История цен для продукта с ID/URL {product_id_or_url} не найдена", status_code=404)


class DatabaseError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Ошибка базы данных: {message}", status_code=500)
