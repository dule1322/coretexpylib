#     Copyright (C) 2023  Coretex LLC

#     This file is part of Coretex.ai

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum


class NodeEnvironment(Enum):

    development = "dev"
    stage       = "stage"
    production  = "production"

    def coretexpylibSource(self) -> str:
        if self == NodeEnvironment.development:
            branch = "develop"
        elif self == NodeEnvironment.stage:
            branch = "stage"
        elif self == NodeEnvironment.production:
            branch = "main"

        return f"git+https://github.com/coretex-ai/coretexpylib@{branch}#egg=coretex"
