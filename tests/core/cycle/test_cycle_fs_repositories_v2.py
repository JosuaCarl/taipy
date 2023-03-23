# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os

import pytest

from src.taipy.core.cycle._cycle_fs_repository_v2 import _CycleFSRepository
from src.taipy.core.cycle.cycle import Cycle
from src.taipy.core.exceptions import ModelNotFound
from taipy.core import CycleId


class TestCycleFSRepository:
    def test_save_and_load(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir
        repository._save(cycle)

        obj = repository._load(cycle.id)
        assert isinstance(obj, Cycle)

    def test_load_all(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir
        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            repository._save(cycle)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    def test_load_all_with_filters(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            cycle.name = f"cycle-{i}"
            repository._save(cycle)
        objs = repository._load_all(filters=[{"name": "cycle-2"}])

        assert len(objs) == 1

    def test_delete(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir
        repository._save(cycle)

        repository._delete(cycle.id)

        with pytest.raises(ModelNotFound):
            repository._load(cycle.id)

    def test_delete_all(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            repository._save(cycle)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    def test_delete_many(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            repository._save(cycle)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    def test_search(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            cycle.name = f"cycle-{i}"
            repository._save(cycle)

        assert len(repository._load_all()) == 10

        obj = repository._search("name", "cycle-2")

        assert isinstance(obj, Cycle)

    def test_export(self, tmpdir, cycle):
        repository = _CycleFSRepository()
        repository.base_path = tmpdir
        repository._save(cycle)

        repository._export(cycle.id, tmpdir.strpath)
        assert os.path.exists(os.path.join(repository.dir_path, f"{cycle.id}.json"))
