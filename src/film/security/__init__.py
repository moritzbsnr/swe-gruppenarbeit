# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Modul für den Zugriffsschutz."""

from film.security.auth_router import router, token
from film.security.exceptions import AuthorizationError, LoginError
from film.security.response_headers import set_response_headers
from film.security.role import Role
from film.security.roles_required import RolesRequired
from film.security.token_service import TokenService
from film.security.user import User
from film.security.user_service import UserService

__all__ = [
    "AuthorizationError",
    "LoginError",
    "Role",
    "RolesRequired",
    "TokenService",
    "User",
    "UserService",
    "router",
    "set_response_headers",
    "token",
]
