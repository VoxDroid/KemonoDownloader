import os

from kemonodownloader import creator_downloader as cd


class DummySettingsTab:
    def __init__(self, template=None, strategy=None):
        self._template = template
        self._strategy = strategy

    def get_creator_filename_template(self):
        return self._template

    def get_creator_folder_strategy(self):
        return self._strategy


class DummySettings:
    def __init__(self, settings_tab):
        self.settings_tab = settings_tab


def test_sanitize_filename_various():
    assert cd.sanitize_filename("") == "unnamed"
    assert cd.sanitize_filename("...hidden") == "hidden"
    assert cd.sanitize_filename("a <>:b|c?*d") == "a_b_c_d"
    assert cd.sanitize_filename("  spaced name  ") == "spaced_name"


def test_get_user_agent_fallback(monkeypatch):
    orig_UserAgent = cd.UserAgent

    class BadUA:
        def __init__(self):
            raise Exception("no UA")

    monkeypatch.setattr(cd, "UserAgent", BadUA)
    cd._user_agent = None
    ua = cd.get_user_agent()
    assert "Mozilla/5.0" in ua
    # restore (monkeypatch will revert automatically, but be explicit)
    monkeypatch.setattr(cd, "UserAgent", orig_UserAgent)


def test_generate_filename_and_folder(tmp_path):
    settings_tab = DummySettingsTab(
        template="{post_id}_{orig_name}", strategy="per_post"
    )
    settings = DummySettings(settings_tab)
    service = "fanbox"
    creator_id = "123"
    download_folder = str(tmp_path)
    selected_posts = ["1"]
    files_to_download = ["https://kemono.cr/files/download.jpg?f=orig_name.jpg"]
    files_to_posts_map = {files_to_download[0]: "1"}
    console = None
    other_files_dir = str(tmp_path / "other")
    post_titles_map = {}

    thread = cd.CreatorDownloadThread(
        service,
        creator_id,
        download_folder,
        selected_posts,
        files_to_download,
        files_to_posts_map,
        console,
        other_files_dir,
        post_titles_map,
        auto_rename_enabled=False,
        settings=settings,
        max_concurrent=1,
    )
    thread.creator_name = "Creator Name"
    target_folder, filename = thread.generate_filename_and_folder(
        files_to_download[0], download_folder, 0, 1, "1", "Post Title"
    )
    assert "123_Creator Name" in target_folder
    assert filename.endswith(".jpg")

    # test auto_rename increments prefix
    thread2 = cd.CreatorDownloadThread(
        service,
        creator_id,
        download_folder,
        selected_posts,
        files_to_download,
        files_to_posts_map,
        console,
        other_files_dir,
        post_titles_map,
        auto_rename_enabled=True,
        settings=settings,
        max_concurrent=1,
    )
    thread2.creator_name = "Creator Name"
    tf1, fn1 = thread2.generate_filename_and_folder(
        files_to_download[0], download_folder, 0, 1, "1", "Post Title"
    )
    tf2, fn2 = thread2.generate_filename_and_folder(
        files_to_download[0], download_folder, 1, 1, "1", "Post Title"
    )
    assert fn1 != fn2


def test_generate_folder_strategies(tmp_path):
    settings_tab = DummySettingsTab(
        template="{post_id}_{orig_name}", strategy="by_file_type"
    )
    settings = DummySettings(settings_tab)
    service = "fanbox"
    creator_id = "123"
    download_folder = str(tmp_path)
    selected_posts = ["1"]
    files_to_download = ["https://kemono.cr/files/path/file.png"]
    files_to_posts_map = {files_to_download[0]: "1"}
    console = None
    other_files_dir = str(tmp_path / "other")
    post_titles_map = {}

    thread = cd.CreatorDownloadThread(
        service,
        creator_id,
        download_folder,
        selected_posts,
        files_to_download,
        files_to_posts_map,
        console,
        other_files_dir,
        post_titles_map,
        auto_rename_enabled=False,
        settings=settings,
        max_concurrent=1,
    )
    thread.creator_name = "Creator Name"
    target_folder, filename = thread.generate_filename_and_folder(
        files_to_download[0], download_folder, 0, 1, "1", "Post Title"
    )
    # expecting extension folder under creator folder
    # creator_name is used verbatim in folder construction
    assert os.path.join(
        "123_Creator Name", "png"
    ) in target_folder or target_folder.endswith(
        os.path.join("123_Creator Name", "png")
    )

    # single_folder strategy
    settings_tab2 = DummySettingsTab(template=None, strategy="single_folder")
    settings2 = DummySettings(settings_tab2)
    thread2 = cd.CreatorDownloadThread(
        service,
        creator_id,
        download_folder,
        selected_posts,
        files_to_download,
        files_to_posts_map,
        console,
        other_files_dir,
        post_titles_map,
        auto_rename_enabled=False,
        settings=settings2,
        max_concurrent=1,
    )
    thread2.creator_name = "Creator Name"
    target_folder2, filename2 = thread2.generate_filename_and_folder(
        files_to_download[0], download_folder, 0, 1, "1", "Post Title"
    )
    assert target_folder2.endswith(os.path.join("123_Creator Name"))


def test_preview_thread_cache_hit(tmp_path):
    import hashlib

    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap

    url = "https://kemono.cr/uploads/preview.jpg"
    cache_dir = str(tmp_path / "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_key = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(url)[1]
    cache_path = os.path.join(cache_dir, cache_key)

    pix = QPixmap(10, 10)
    pix.fill(Qt.GlobalColor.white)
    assert pix.save(cache_path)

    thread = cd.PreviewThread(url, cache_dir)
    results = {}

    def on_preview(u, p):
        results["url"] = u
        results["pix"] = p

    thread.preview_ready.connect(on_preview)
    # run synchronously
    thread.run()
    assert results.get("url") == url
    assert isinstance(results.get("pix"), QPixmap)


def test_post_population_and_filter_and_checkbox_threads():
    # PostPopulationThread
    detected = [("TitleA", ("1", "http://x")), ("TitleB", ("2", None))]
    ppop = cd.PostPopulationThread(detected)
    pop_res = {}

    def on_pop_finished(mapping, posts):
        pop_res["mapping"] = mapping
        pop_res["posts"] = posts

    ppop.finished.connect(on_pop_finished)
    ppop.run()
    assert any("TitleA" in k for k in pop_res["mapping"].keys())

    # FilterThread
    ft = cd.FilterThread(
        detected, checked_urls={"1": True, "2": False}, search_text="titlea"
    )
    filt_res = {}

    def on_filter_finished(items):
        filt_res["items"] = items

    ft.finished.connect(on_filter_finished)
    ft.run()
    assert any("TitleA" in t[0] for t in filt_res["items"])

    # CheckboxToggleThread
    visible = [("TitleA", ("1", None)), ("TitleB", ("2", None))]
    checked = {"1": False, "2": False}
    ctt = cd.CheckboxToggleThread(visible, checked, check_all_state=2)
    c_res = {}

    def on_checkbox_finished(new_checked, posts_to_download):
        c_res["checked"] = new_checked
        c_res["posts"] = posts_to_download

    ctt.finished.connect(on_checkbox_finished)
    ctt.run()
    assert "1" in c_res["checked"] and c_res["checked"]["1"] is True
    assert "1" in c_res["posts"]


def test_detect_files_main_attachments_content(tmp_path):
    # Prepare fake checkboxes that indicate which extensions are enabled
    class FakeCheckbox:
        def __init__(self, checked=True):
            self._checked = checked

        def isChecked(self):
            return self._checked

    creator_ext_checks = {
        ".png": FakeCheckbox(True),
        ".jpg": FakeCheckbox(True),
        ".gif": FakeCheckbox(True),
    }
    settings = DummySettings(None)
    fthread = cd.FilePreparationThread(
        post_ids=[],
        all_files_map={},
        creator_ext_checks=creator_ext_checks,
        creator_main_check=True,
        creator_attachments_check=True,
        creator_content_check=True,
        settings=settings,
        max_concurrent=1,
    )

    post = {
        "file": {"path": "/uploads/image.jpg", "name": "image.jpg"},
        "attachments": [{"path": "/uploads/attach.png", "name": "attach.png"}],
        "content": '<p>Hi<img src="/uploads/content.gif"/></p>',
    }
    domain_config = cd.get_domain_config("https://kemono.cr/")
    allowed = [".png", ".jpg", ".gif"]
    files = fthread.detect_files(post, allowed, domain_config)
    # Should detect main file, attachment and content image
    names = [n for n, _ in files]
    assert "image.jpg" in names
    assert "attach.png" in names
    assert "content.gif" in names


def test_get_session_with_socks(monkeypatch):
    # Clear any existing thread-local sessions
    if hasattr(cd._thread_local, "session"):
        delattr(cd._thread_local, "session")
    if hasattr(cd._thread_local, "socks_session"):
        delattr(cd._thread_local, "socks_session")

    class FakeSettingsTabObj:
        def get_proxy_settings(self):
            return {
                "http": "socks5://127.0.0.1:1080",
                "https": "socks5://127.0.0.1:1080",
            }

    s = FakeSettingsTabObj()
    sess = cd.get_session(s)
    import requests as _req

    assert isinstance(sess, _req.sessions.Session)
    # proxies should be set on the returned session
    assert sess.proxies.get("http") == "socks5://127.0.0.1:1080"
