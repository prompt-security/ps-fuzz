from ps_fuzz.attacks import utils


def test_packaged_attack_data_path_exposes_shipped_dataset():
    """The installed package must provide attack data without pkg_resources."""
    with utils.packaged_attack_data_path("harmful_behavior.csv") as dataset_path:
        assert dataset_path.is_file()
        assert dataset_path.name == "harmful_behavior.csv"
        assert dataset_path.read_text(encoding="utf-8").startswith("goal,target")
