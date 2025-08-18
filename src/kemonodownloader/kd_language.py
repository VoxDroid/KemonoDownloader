class KDLanguage:
    """
    Language management class for Kemono Downloader.
    Provides translations for all text in the application.
    Supports English (default), Japanese, Korean and Simplified Chinese.
    """
    
    def __init__(self):
        self.current_language = "english"  # Default language
        self.translations = {
            
            "downloading": {
                "english": "Downloading",
                "japanese": "ダウンロード中",
                "korean": "다운로드 중",
                "chinese-simplified": "下载中"
            },
            "completed": {
                "english": "Completed",
                "japanese": "完了",
                "korean": "완료",
                "chinese-simplified": "已完成"
            },
            "failed": {
                "english": "Failed",
                "japanese": "失敗",
                "korean": "실패",
                "chinese-simplified": "失败"
            },
            "auto_rename": {
                "english": "Auto Rename and sort File name by order",
                "japanese": "自動リネームとファイル名を順序で並べ替え",
                "korean": "자동 이름 바꾸기 및 순서별 파일 이름 정렬",
                "chinese-simplified": "自动重命名并按顺序排序文件名"
            },

            "open_directory": {
                "english": "Open Directory",
                "japanese": "ディレクトリを開く",
                "korean": "디렉토리 열기",
                "chinese-simplified": "打开目录"
            },
            
            "download_failed_retrying": {
                "english": "Download failed for {0}, attempt {1}/{2}: {3}",
                "japanese": "{0}のダウンロードに失敗しました、試行{1}/{2}：{3}",
                "korean": "{0} 다운로드 실패, 시도 {1}/{2}: {3}",
                "chinese-simplified": "{0}下载失败，尝试 {1}/{2}: {3}"
            },
            "error_downloading_after_retries": {
                "english": "Failed to download {0} after {1} retries: {2}",
                "japanese": "{1}回の試行後に{0}のダウンロードに失敗しました：{2}",
                "korean": "{1}번의 시도 후 {0} 다운로드 실패: {2}",
                "chinese-simplified": "尝试 {1} 次后下载 {0} 失败: {2}"
            },
            "retry_countdown": {
                "english": "Trying again in {0}...",
                "japanese": "{0}秒後に再試行します...",
                "korean": "{0}초 후 다시 시도...",
                "chinese-simplified": "{0}秒后重试..."
            },
            
            # Reset to defaults translation
            "reset_to_defaults" : {
                "english" : "Reset to Defaults",
                "japanese" : "デフォルトにリセット",
                "korean" : "기본값으로 재설정",
                "chinese-simplified" : "重置为默认值"
            },
            "confirm_reset_message" : {
                "english" : "Are you sure you want to reset all settings to their default values?",
                "japanese" : "すべての設定をデフォルト値にリセットしてもよろしいですか？",
                "korean" : "모든 설정을 기본값으로 재설정하시겠습니까?",
                "chinese-simplified" : "您确定要将所有设置重置为默认值吗？"
            },
            "settings_reset_message" : {
                "english" : "Settings have been reset to defaults. Click 'Apply Changes' to save them.",
                "japanese" : "設定がデフォルトにリセットされました。'変更を適用'をクリックして保存してください。",
                "korean" : "설정이 기본값으로 재설정되었습니다. '변경 적용'을 클릭하여 저장하세요.",
                "chinese-simplified" : "设置已重置为默认值。单击“应用更改”以保存它们。"
            },
            
            # For post_downloader.py fallback validation
            "first_validation_failed": {
                "english": "First validation method failed for {0}, trying fallback method...",
                "japanese": "最初の検証方法が {0} で失敗しました、フォールバック方法を試しています...",
                "korean": "첫 번째 검증 방법이 {0}에 대해 실패했습니다, 대체 방법을 시도 중...",
                "chinese-simplified": "第一次验证方法失败。尝试备用方法..."
            },
            "first_validation_failed_exception": {
                "english": "First validation method failed with exception for {0}, trying fallback method...",
                "japanese": "最初の検証方法が {0} で例外で失敗しました、フォールバック方法を試しています...",
                "korean": "첫 번째 검증 방법이 {0}에 대해 예외로 실패했습니다, 대체 방법을 시도 중...",
                "chinese-simplified": "第一次验证方法失败：{0}尝试备用方法..."
            },
            "attempting_fallback_validation": {
                "english": "Attempting fallback validation for {0}",
                "japanese": "{0} のフォールバック検証を試みています",
                "korean": "{0}에 대한 대체 검증 시도 중",
                "chinese-simplified": "尝试备用验证：{0}"
            },
            "url_validated_fallback": {
                "english": "URL validated using fallback method: {0}",
                "japanese": "フォールバック方法を使用してURLが検証されました: {0}",
                "korean": "대체 방법을 사용하여 URL이 검증됨: {0}",
                "chinese-simplified": "使用备用方法验证的 URL：{0}"
            },
            "fallback_validation_failed": {
                "english": "Fallback validation failed with exception: {0}",
                "japanese": "フォールバック検証が例外で失敗しました: {0}",
                "korean": "대체 검증이 예외로 실패했습니다: {0}",
                "chinese-simplified": "备用验证失败：{0}"
            },

            # For creator_downloader.py fallback validation
            "first_validation_failed": {
                "english": "First validation method failed for {0}, trying fallback method...",
                "japanese": "最初の検証方法が {0} で失敗しました、フォールバック方法を試しています...",
                "korean": "첫 번째 검증 방법이 {0}에 대해 실패했습니다, 대체 방법을 시도 중...",
                "chinese-simplified": "第一次验证方法失败。尝试备用方法..."
            },
            "first_validation_failed_exception": {
                "english": "First validation method failed with exception for {0}, trying fallback method...",
                "japanese": "最初の検証方法が {0} で例外で失敗しました、フォールバック方法を試しています...",
                "korean": "첫 번째 검증 방법이 {0}에 대해 예외로 실패했습니다, 대체 방법을 시도 중...",
                "chinese-simplified": "第一次验证方法失败：{0}尝试备用方法..."
            },
            "attempting_fallback_validation": {
                "english": "Attempting fallback validation for {0}",
                "japanese": "{0} のフォールバック検証を試みています",
                "korean": "{0}에 대한 대체 검증 시도 중",
                "chinese-simplified": "尝试备用验证：{0}"
            },
            "url_validated_fallback": {
                "english": "URL validated using fallback method: {0}",
                "japanese": "フォールバック方法を使用してURLが検証されました: {0}",
                "korean": "대체 방법을 사용하여 URL이 검증됨: {0}",
                "chinese-simplified": "使用备用方法验证的 URL：{0}"
            },
            "fallback_validation_failed": {
                "english": "Fallback validation failed with exception: {0}",
                "japanese": "フォールバック検証が例外で失敗しました: {0}",
                "korean": "대체 검증이 예외로 실패했습니다: {0}",
                "chinese-simplified": "备用验证失败：{0}"
            },
            
            # Main window and common elements
            "app_title": {
                "english": "Kemono Downloader",
                "japanese": "ケモノダウンローダー",
                "korean": "케모노 다운로더",
                "chinese-simplified": "Kemono 下载器"
            },
            "developed_by": {
                "english": "Developed by VoxDroid",
                "japanese": "開発者: VoxDroid",
                "korean": "개발자: VoxDroid",
                "chinese-simplified": "开发者: VoxDroid"
            },
            "launch_button": {
                "english": "Launch Application",
                "japanese": "アプリケーションを起動",
                "korean": "애플리케이션 시작",
                "chinese-simplified": "启动应用程序"
            },
            "idle": {
                "english": "Idle",
                "japanese": "アイドル",
                "korean": "대기 중",
                "chinese-simplified": "空闲"
            },
            
            # Tab names
            "post_downloader_tab": {
                "english": "Post Downloader",
                "japanese": "投稿ダウンローダー",
                "korean": "게시물 다운로더",
                "chinese-simplified": "投稿下载器"
            },
            "creator_downloader_tab": {
                "english": "Creator Downloader",
                "japanese": "クリエイターダウンローダー",
                "korean": "크리에이터 다운로더",
                "chinese-simplified": "创作者下载器"
            },
            "settings_tab": {
                "english": "Settings",
                "japanese": "設定",
                "korean": "설정",
                "chinese-simplified": "设置"
            },
            "help_tab": {
                "english": "Help",
                "japanese": "ヘルプ",
                "korean": "도움말",
                "chinese-simplified": "帮助"
            },
            
            # Common buttons and actions
            "add_to_queue": {
                "english": "Add to Queue",
                "japanese": "キューに追加",
                "korean": "대기열에 추가",
                "chinese-simplified": "添加到队列"
            },
            "download": {
                "english": "Download",
                "japanese": "ダウンロード",
                "korean": "다운로드",
                "chinese-simplified": "下载"
            },
            "cancel": {
                "english": "Cancel",
                "japanese": "キャンセル",
                "korean": "취소",
                "chinese-simplified": "取消"
            },
            "apply_changes": {
                "english": "Apply Changes",
                "japanese": "変更を適用",
                "korean": "변경 적용",
                "chinese-simplified": "应用更改"
            },
            "browse": {
                "english": "Browse",
                "japanese": "参照",
                "korean": "찾아보기",
                "chinese-simplified": "浏览"
            },
            
            # Post Downloader tab
            "enter_post_url": {
                "english": "Enter post URL (e.g., https://kemono.cr/patreon/user/12345678/post/123456789)",
                "japanese": "投稿URLを入力 (例: https://kemono.cr/patreon/user/12345678/post/123456789)",
                "korean": "게시물 URL 입력 (예: https://kemono.cr/patreon/user/12345678/post/123456789)",
                "chinese-simplified": "输入投稿 URL (例如: https://kemono.cr/patreon/user/12345678/post/123456789)"
            },
            "post_queue": {
                "english": "Post Queue",
                "japanese": "投稿キュー",
                "korean": "게시물 대기열",
                "chinese-simplified": "投稿队列"
            },
            "files_to_download": {
                "english": "Files to Download",
                "japanese": "ダウンロードするファイル",
                "korean": "다운로드할 파일",
                "chinese-simplified": "将要下载的文件"
            },
            "filter_by_type": {
                "english": "Filter by Type",
                "japanese": "タイプでフィルタリング",
                "korean": "유형별 필터링",
                "chinese-simplified": "按类型过滤"
            },
            "search_items": {
                "english": "Search items...",
                "japanese": "アイテムを検索...",
                "korean": "항목 검색...",
                "chinese-simplified": "搜索项目..."
            },
            "check_all": {
                "english": "Check ALL",
                "japanese": "すべてチェック",
                "korean": "모두 선택",
                "chinese-simplified": "全选"
            },
            "download_all_links": {
                "english": "Download All Links",
                "japanese": "すべてのリンクをダウンロード",
                "korean": "모든 링크 다운로드",
                "chinese-simplified": "下载所有链接"
            },
            "files_count": {
                "english": "Files: {0}",
                "japanese": "ファイル: {0}",
                "korean": "파일: {0}",
                "chinese-simplified": "文件: {0}"
            },
            "file_progress": {
                "english": "File Progress {0}%",
                "japanese": "ファイル進捗 {0}%",
                "korean": "파일 진행률 {0}%",
                "chinese-simplified": "文件进度 {0}%"
            },
            "overall_progress": {
                "english": "Overall Progress ({0}/{1} files, {2}/{3} posts)",
                "japanese": "全体の進捗 ({0}/{1} ファイル, {2}/{3} 投稿)",
                "korean": "전체 진행률 ({0}/{1} 파일, {2}/{3} 게시물)",
                "chinese-simplified": "整体进度 ({0}/{1} 文件, {2}/{3} 投稿)"
            },
            
            # Creator Downloader tab
            "enter_creator_url": {
                "english": "Enter creator URL (e.g., https://kemono.cr/patreon/user/12345678)",
                "japanese": "クリエイターURLを入力 (例: https://kemono.cr/patreon/user/12345678)",
                "korean": "크리에이터 URL 입력 (예: https://kemono.cr/patreon/user/12345678)",
                "chinese-simplified": "输入创作者 URL (例如: https://kemono.cr/patreon/user/12345678)"
            },
            "creator_queue": {
                "english": "Creator Queue",
                "japanese": "クリエイターキュー",
                "korean": "크리에이터 대기열",
                "chinese-simplified": "创作者队列"
            },
            "download_options": {
                "english": "Download Options",
                "japanese": "ダウンロードオプション",
                "korean": "다운로드 옵션",
                "chinese-simplified": "下载选项"
            },
            "main_file": {
                "english": "Main File",
                "japanese": "メインファイル",
                "korean": "메인 파일",
                "chinese-simplified": "主要文件"
            },
            "attachments": {
                "english": "Attachments",
                "japanese": "添付ファイル",
                "korean": "첨부 파일",
                "chinese-simplified": "附件"
            },
            "content_images": {
                "english": "Content Images",
                "japanese": "コンテンツ画像",
                "korean": "콘텐츠 이미지",
                "chinese-simplified": "内容图片"
            },
            "file_extensions": {
                "english": "File Extensions",
                "japanese": "ファイル拡張子",
                "korean": "파일 확장자",
                "chinese-simplified": "文件扩展名"
            },
            "posts_to_download": {
                "english": "Posts to Download",
                "japanese": "ダウンロードする投稿",
                "korean": "다운로드할 게시물",
                "chinese-simplified": "将要下载的投稿"
            },
            "search_posts": {
                "english": "Search posts...",
                "japanese": "投稿を検索...",
                "korean": "게시물 검색...",
                "chinese-simplified": "搜索投稿..."
            },
            "posts_count": {
                "english": "Posts: {0}",
                "japanese": "投稿: {0}",
                "korean": "게시물: {0}",
                "chinese-simplified": "投稿: {0}"
            },
            
            # Settings tab
            "folder_settings": {
                "english": "Folder Settings",
                "japanese": "フォルダ設定",
                "korean": "폴더 설정",
                "chinese-simplified": "文件夹设置"
            },
            "folder_name": {
                "english": "Folder Name:",
                "japanese": "フォルダ名:",
                "korean": "폴더 이름:",
                "chinese-simplified": "文件夹名称:"
            },
            "save_directory": {
                "english": "Save Directory:",
                "japanese": "保存ディレクトリ:",
                "korean": "저장 디렉토리:",
                "chinese-simplified": "保存目录:"
            },
            "download_settings": {
                "english": "Download Settings",
                "japanese": "ダウンロード設定",
                "korean": "다운로드 설정",
                "chinese-simplified": "下载设置"
            },
            "simultaneous_downloads": {
                "english": "Simultaneous Downloads:",
                "japanese": "同時ダウンロード数:",
                "korean": "동시 다운로드:",
                "chinese-simplified": "并行下载数:"
            },
            "update_settings": {
                "english": "Update Settings",
                "japanese": "更新設定",
                "korean": "업데이트 설정",
                "chinese-simplified": "更新设置"
            },
            "auto_check_updates": {
                "english": "Auto Check for Updates:",
                "japanese": "自動更新チェック:",
                "korean": "자동 업데이트 확인:",
                "chinese-simplified": "自动检查更新:"
            },
            "language_settings": {
                "english": "Language Settings",
                "japanese": "言語設定",
                "korean": "언어 설정",
                "chinese-simplified": "语言设置"
            },
            "language": {
                "english": "Language:",
                "japanese": "言語:",
                "korean": "언어:",
                "chinese-simplified": "语言:"
            },
            "english": {
                "english": "English",
                "japanese": "英語",
                "korean": "영어",
                "chinese-simplified": "英语"
            },
            "japanese": {
                "english": "Japanese",
                "japanese": "日本語",
                "korean": "일본어",
                "chinese-simplified": "日语"
            },
            "korean": {
                "english": "Korean",
                "japanese": "韓国語",
                "korean": "한국어",
                "chinese-simplified": "韩语"
            },
            "chinese-simplified": {
                "english": "Chinese (Simplified)",
                "japanese": "中国語 (簡体字)",
                "korean": "중국어 (간체)",
                "chinese-simplified": "中文 (简体)"
            },

            "expand_logs": {
                "english": "Expand Logs",
                "japanese": "ログを展開",
                "korean": "로그 확장",
                "chinese-simplified": "展开日志"
            },
            "full_logs": {
                "english": "Full Logs",
                "japanese": "完全なログ",
                "korean": "전체 로그",
                "chinese-simplified": "完整日志"
            },
            "clear_logs": {
                "english": "Clear Logs",
                "japanese": "ログをクリア",
                "korean": "로그 지우기",
                "chinese-simplified": "清除日志"
            },
            "download_logs": {
                "english": "Download Logs",
                "japanese": "ログをダウンロード",
                "korean": "로그 다운로드",
                "chinese-simplified": "下载日志"
            },
            
            # Confirmation dialogs
            "confirm_settings_change": {
                "english": "Confirm Settings Change",
                "japanese": "設定変更の確認",
                "korean": "설정 변경 확인",
                "chinese-simplified": "确认设置更改"
            },
            "confirm_settings_message": {
                "english": "Are you sure you want to apply these settings?\n\nFolder Name: {0}\nSave Directory: {1}\nSimultaneous Downloads: {2}\nAuto Check Updates: {3}\nLanguage: {4}",
                "japanese": "これらの設定を適用してもよろしいですか？\n\nフォルダ名: {0}\n保存ディレクトリ: {1}\n同時ダウンロード数: {2}\n自動更新チェック: {3}\n言語: {4}",
                "korean": "이 설정을 적용하시겠습니까?\n\n폴더 이름: {0}\n저장 디렉토리: {1}\n동시 다운로드: {2}\n자동 업데이트 확인: {3}\n언어: {4}",
                "chinese-simplified": "您确定要应用这些设置吗？\n\n文件夹名称: {0}\n保存目录: {1}\n并行下载数: {2}\n自动检查更新: {3}\n语言: {4}"
            },
            "enabled": {
                "english": "Enabled",
                "japanese": "有効",
                "korean": "활성화",
                "chinese-simplified": "启用"
            },
            "disabled": {
                "english": "Disabled",
                "japanese": "無効",
                "korean": "비활성화",
                "chinese-simplified": "禁用"
            },
            "yes": {
                "english": "Yes",
                "japanese": "はい",
                "korean": "예",
                "chinese-simplified": "是"
            },
            "no": {
                "english": "No",
                "japanese": "いいえ",
                "korean": "아니오",
                "chinese-simplified": "否"
            },
            "ok": {
                "english": "OK",
                "japanese": "OK",
                "korean": "확인",
                "chinese-simplified": "确定"
            },
            "settings_applied": {
                "english": "Settings Applied",
                "japanese": "設定が適用されました",
                "korean": "설정 적용됨",
                "chinese-simplified": "设置已应用"
            },
            "settings_applied_message": {
                "english": "Settings have been successfully applied!\n\nFolder Name: {0}\nSave Directory: {1}\nSimultaneous Downloads: {2}\nAuto Check Updates: {3}\nLanguage: {4}",
                "japanese": "設定が正常に適用されました！\n\nフォルダ名: {0}\n保存ディレクトリ: {1}\n同時ダウンロード数: {2}\n自動更新チェック: {3}\n言語: {4}",
                "korean": "설정이 성공적으로 적용되었습니다!\n\n폴더 이름: {0}\n저장 디렉토리: {1}\n동시 다운로드: {2}\n자동 업데이트 확인: {3}\n언어: {4}",
                "chinese-simplified": "设置已成功应用！\n\n文件夹名称: {0}\n保存目录: {1}\n并行下载数: {2}\n自动检查更新: {3}\n语言: {4}"
            },
            "confirm_removal": {
                "english": "Confirm Removal",
                "japanese": "削除の確認",
                "korean": "제거 확인",
                "chinese-simplified": "确认删除"
            },
            "confirm_removal_message": {
                "english": "Are you sure you want to remove {0} from the queue?",
                "japanese": "キューから {0} を削除してもよろしいですか？",
                "korean": "대기열에서 {0}을(를) 제거하시겠습니까?",
                "chinese-simplified": "您确定要从队列中删除 {0} 吗？"
            },
            
            # Error messages
            "invalid_input": {
                "english": "Invalid Input",
                "japanese": "無効な入力",
                "korean": "잘못된 입력",
                "chinese-simplified": "无效输入"
            },
            "folder_name_empty": {
                "english": "Folder name cannot be empty.",
                "japanese": "フォルダ名は空にできません。",
                "korean": "폴더 이름은 비워둘 수 없습니다.",
                "chinese-simplified": "文件夹名称不能为空。"
            },
            "directory_not_exist": {
                "english": "Selected directory does not exist.",
                "japanese": "選択したディレクトリが存在しません。",
                "korean": "선택한 디렉토리가 존재하지 않습니다.",
                "chinese-simplified": "所选目录不存在。"
            },
            "update_check_failed": {
                "english": "Update Check Failed",
                "japanese": "更新チェックに失敗しました",
                "korean": "업데이트 확인 실패",
                "chinese-simplified": "检查更新失败"
            },
            "unable_check_updates": {
                "english": "Unable to check for updates.",
                "japanese": "更新を確認できません。",
                "korean": "업데이트를 확인할 수 없습니다.",
                "chinese-simplified": "无法检查更新。"
            },
            "image_load_error": {
                "english": "Image Load Error",
                "japanese": "画像読み込みエラー",
                "korean": "이미지 로드 오류",
                "chinese-simplified": "图片加载错误"
            },
            "media_load_error": {
                "english": "Media Load Error",
                "japanese": "メディア読み込みエラー",
                "korean": "미디어 로드 오류",
                "chinese-simplified": "媒体加载错误"
            },
            
            # Update notification
            "update_available": {
                "english": "Update Available",
                "japanese": "更新があります",
                "korean": "업데이트 가능",
                "chinese-simplified": "更新可用"
            },
            "update_available_message": {
                "english": "A new version ({0}) is available!",
                "japanese": "新しいバージョン ({0}) が利用可能です！",
                "korean": "새 버전({0})이 사용 가능합니다!",
                "chinese-simplified": "新版本 ({0}) 可用！"
            },
            "current_version": {
                "english": "Current version: {0}",
                "japanese": "現在のバージョン: {0}",
                "korean": "현재 버전: {0}",
                "chinese-simplified": "当前版本: {0}"
            },
            "click_release_page": {
                "english": "Click here to visit the release page",
                "japanese": "リリースページを訪問するにはここをクリック",
                "korean": "릴리스 페이지를 방문하려면 여기를 클릭하세요",
                "chinese-simplified": "点击此处访问发布页面"
            },
            
            # Background tasks
            "detecting_post": {
                "english": "Detecting post from link...",
                "japanese": "リンクから投稿を検出中...",
                "korean": "링크에서 게시물 감지 중...",
                "chinese-simplified": "从链接检测投稿..."
            },
            "detecting_posts": {
                "english": "Detecting posts from link...",
                "japanese": "リンクから投稿を検出中...",
                "korean": "링크에서 게시물 감지 중...",
                "chinese-simplified": "从链接检测投稿..."
            },
            "validating_url": {
                "english": "Validating URL...",
                "japanese": "URLを検証中...",
                "korean": "URL 검증 중...",
                "chinese-simplified": "验证 URL..."
            },
            "populating_posts": {
                "english": "Populating posts...",
                "japanese": "投稿を読み込み中...",
                "korean": "게시물 채우는 중...",
                "chinese-simplified": "添加投稿信息..."
            },
            "filtering_posts": {
                "english": "Filtering posts...",
                "japanese": "投稿をフィルタリング中...",
                "korean": "게시물 필터링 중...",
                "chinese-simplified": "过滤投稿..."
            },
            "preparing_files": {
                "english": "Preparing files to download...",
                "japanese": "ダウンロードするファイルを準備中...",
                "korean": "다운로드할 파일 준비 중...",
                "chinese-simplified": "准备下载文件..."
            },
            "updating_checkboxes": {
                "english": "Updating checkboxes...",
                "japanese": "チェックボックスを更新中...",
                "korean": "체크박스 업데이트 중...",
                "chinese-simplified": "更新复选框..."
            },
            "updating_download_mode": {
                "english": "Updating download mode...",
                "japanese": "ダウンロードモードを更新中...",
                "korean": "다운로드 모드 업데이트 중...",
                "chinese-simplified": "更新下载模式..."
            },
            "toggling_checkbox": {
                "english": "Toggling checkbox...",
                "japanese": "チェックボックスを切り替え中...",
                "korean": "체크박스 토글 중...",
                "chinese-simplified": "切换复选框..."
            },
            "loading_image": {
                "english": "Loading Image... ({0}%)",
                "japanese": "画像を読み込み中... ({0}%)",
                "korean": "이미지 로드 중... ({0}%)",
                "chinese-simplified": "加载图片... ({0}%)"
            },
            "loading_image_simple": {
                "english": "Loading Image...",
                "japanese": "画像を読み込み中...",
                "korean": "이미지 로드 중...",
                "chinese-simplified": "加载图片..."
            },
            "error_loading_image": {
                "english": "Error loading image",
                "japanese": "画像の読み込みエラー",
                "korean": "이미지 로드 오류",
                "chinese-simplified": "加载图片时出错"
            },
            
            # Log messages
            "log_info": {
                "english": "[INFO] {0}",
                "japanese": "[情報] {0}",
                "korean": "[정보] {0}",
                "chinese-simplified": "[消息] {0}"
            },
            "log_warning": {
                "english": "[WARNING] {0}",
                "japanese": "[警告] {0}",
                "korean": "[경고] {0}",
                "chinese-simplified": "[警告] {0}"
            },
            "log_error": {
                "english": "[ERROR] {0}",
                "japanese": "[エラー] {0}",
                "korean": "[오류] {0}",
                "chinese-simplified": "[错误] {0}"
            },
            "log_debug": {
                "english": "[DEBUG] {0}",
                "japanese": "[デバッグ] {0}",
                "korean": "[디버그] {0}",
                "chinese-simplified": "[调试] {0}"
            },
            
            # Common log messages
            "no_url_entered": {
                "english": "No URL entered.",
                "japanese": "URLが入力されていません。",
                "korean": "URL이 입력되지 않았습니다.",
                "chinese-simplified": "未输入 URL。"
            },
            "url_already_in_queue": {
                "english": "URL already in queue.",
                "japanese": "URLはすでにキューにあります。",
                "korean": "URL이 이미 대기열에 있습니다.",
                "chinese-simplified": "URL 已在队列中。"
            },
            "added_post_url": {
                "english": "Added post URL to queue: {0}",
                "japanese": "投稿URLをキューに追加しました: {0}",
                "korean": "게시물 URL을 대기열에 추가했습니다: {0}",
                "chinese-simplified": "已将投稿 URL 添加到队列: {0}"
            },
            "added_creator_url": {
                "english": "Added creator URL to queue: {0}",
                "japanese": "クリエイターURLをキューに追加しました: {0}",
                "korean": "크리에이터 URL을 대기열에 추가했습니다: {0}",
                "chinese-simplified": "已将创作者 URL 添加到队列: {0}"
            },
            "invalid_post_url": {
                "english": "Invalid post URL or failed to fetch: {0}",
                "japanese": "無効な投稿URLまたは取得に失敗しました: {0}",
                "korean": "잘못된 게시물 URL 또는 가져오기 실패: {0}",
                "chinese-simplified": "无效的投稿 URL 或获取失败: {0}"
            },
            "invalid_creator_url": {
                "english": "Invalid creator URL or failed to fetch: {0}",
                "japanese": "無効なクリエイターURLまたは取得に失敗しました: {0}",
                "korean": "잘못된 크리에이터 URL 또는 가져오기 실패: {0}",
                "chinese-simplified": "无效的创作者 URL 或获取失败: {0}"
            },
            "viewing_post": {
                "english": "Viewing post: {0}",
                "japanese": "投稿を表示中: {0}",
                "korean": "게시물 보는 중: {0}",
                "chinese-simplified": "查看投稿: {0}"
            },
            "viewing_creator": {
                "english": "Viewing creator: {0}",
                "japanese": "クリエイターを表示中: {0}",
                "korean": "크리에이터 보는 중: {0}",
                "chinese-simplified": "查看创作者: {0}"
            },
            "link_removed": {
                "english": "Link ({0}) is removed from the queue.",
                "japanese": "リンク ({0}) がキューから削除されました。",
                "korean": "링크 ({0})가 대기열에서 제거되었습니다.",
                "chinese-simplified": "链接 ({0}) 已从队列中删除。"
            },
            "url_not_found": {
                "english": "URL ({0}) not found in queue.",
                "japanese": "URL ({0}) がキューに見つかりません。",
                "korean": "URL ({0})이(가) 대기열에 없습니다.",
                "chinese-simplified": "队列中未找到 URL ({0})。"
            },
            "no_posts_queue": {
                "english": "No posts in queue to download.",
                "japanese": "ダウンロードするキューに投稿がありません。",
                "korean": "다운로드할 게시물이 대기열에 없습니다.",
                "chinese-simplified": "下载队列中没有投稿。"
            },
            "no_creators_queue": {
                "english": "No creators in queue to download.",
                "japanese": "ダウンロードするキューにクリエイターがありません。",
                "korean": "다운로드할 크리에이터가 대기열에 없습니다.",
                "chinese-simplified": "下载队列中没有创作者。"
            },
            "no_files_selected": {
                "english": "No files selected for download.",
                "japanese": "ダウンロードするファイルが選択されていません。",
                "korean": "다운로드할 파일이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的文件。"
            },
            "no_posts_selected": {
                "english": "No posts selected for download.",
                "japanese": "ダウンロードする投稿が選択されていません。",
                "korean": "다운로드할 게시물이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的投稿。"
            },
            "preparing_files_post": {
                "english": "Preparing files for currently viewed post: {0}",
                "japanese": "現在表示中の投稿のファイルを準備中: {0}",
                "korean": "현재 보고 있는 게시물의 파일 준비 중: {0}",
                "chinese-simplified": "正在准备当前查看的投稿的文件: {0}"
            },
            "preparing_files_creator": {
                "english": "Preparing files for currently viewed creator: {0}",
                "japanese": "現在表示中のクリエイターのファイルを準備中: {0}",
                "korean": "현재 보고 있는 크리에이터의 파일 준비 중: {0}",
                "chinese-simplified": "正在准备当前查看的创作者的文件: {0}"
            },
            "preparing_files_all_posts": {
                "english": "Preparing files for all posts in queue",
                "japanese": "キュー内のすべての投稿のファイルを準備中",
                "korean": "대기열의 모든 게시물에 대한 파일 준비 중",
                "chinese-simplified": "正在准备队列中所有投稿的文件"
            },
            "preparing_files_all_creators": {
                "english": "Preparing files for all creators in queue",
                "japanese": "キュー内のすべてのクリエイターのファイルを準備中",
                "korean": "대기열의 모든 크리에이터에 대한 파일 준비 중",
                "chinese-simplified": "正在准备队列中所有创作者的文件"
            },
            "download_all_disabled": {
                "english": "Download All Links disabled. Reverted to current post.",
                "japanese": "すべてのリンクをダウンロードが無効になりました。現在の投稿に戻りました。",
                "korean": "모든 링크 다운로드 비활성화됨. 현재 게시물로 되돌아갔습니다.",
                "chinese-simplified": "下载所有链接已禁用。退回到当前投稿。"
            },
            "download_process_ended": {
                "english": "Download process ended",
                "japanese": "ダウンロードプロセスが終了しました",
                "korean": "다운로드 프로세스 종료",
                "chinese-simplified": "下载任务结束"
            },
            "download_process_completed": {
                "english": "Download process completed",
                "japanese": "ダウンロードプロセスが完了しました",
                "korean": "다운로드 프로세스 완료",
                "chinese-simplified": "下载任务完成"
            },
            "downloads_complete": {
                "english": "Downloads Complete",
                "japanese": "ダウンロード完了",
                "korean": "다운로드 완료",
                "chinese-simplified": "下载完毕"
            },
            "downloads_terminated": {
                "english": "Downloads Terminated",
                "japanese": "ダウンロード中断",
                "korean": "다운로드 중단됨",
                "chinese-simplified": "下载终止"
            },
            "cancelling_downloads": {
                "english": "Cancelling all downloads...",
                "japanese": "すべてのダウンロードをキャンセル中...",
                "korean": "모든 다운로드 취소 중...",
                "chinese-simplified": "正在取消所有下载..."
            },
            "all_downloads_cancelled": {
                "english": "All downloads cancelled by user",
                "japanese": "すべてのダウンロードがユーザーによってキャンセルされました",
                "korean": "모든 다운로드가 사용자에 의해 취소됨",
                "chinese-simplified": "所有下载已被用户取消"
            },
            "preview_not_supported": {
                "english": "Preview not supported for file type: {0} ({1})",
                "japanese": "ファイルタイプのプレビューはサポートされていません: {0} ({1})",
                "korean": "파일 유형에 대한 미리보기가 지원되지 않습니다: {0} ({1})",
                "chinese-simplified": "不支持预览的文件类型: {0} ({1})"
            },
            "no_item_selected": {
                "english": "No item selected for preview.",
                "japanese": "プレビューするアイテムが選択されていません。",
                "korean": "미리보기할 항목이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要预览的项目。"
            },
            "file_already_downloaded": {
                "english": "File {0} already downloaded at {1}, skipping.",
                "japanese": "ファイル {0} はすでに {1} にダウンロードされています。スキップします。",
                "korean": "파일 {0}이(가) 이미 {1}에 다운로드되었습니다. 건너뜁니다.",
                "chinese-simplified": "文件 {0} 已在 {1} 下载，跳过。"
            },
            "starting_download": {
                "english": "Starting download of file {0}/{1}: {2} to {3}",
                "japanese": "ファイル {0}/{1} のダウンロードを開始: {2} を {3} に",
                "korean": "파일 {0}/{1} 다운로드 시작: {2}을(를) {3}에",
                "chinese-simplified": "开始下载文件 {0}/{1}: {2} 到 {3}"
            },
            "successfully_downloaded": {
                "english": "Successfully downloaded: {0}",
                "japanese": "ダウンロード成功: {0}",
                "korean": "다운로드 성공: {0}",
                "chinese-simplified": "下载成功: {0}"
            },
            "download_interrupted": {
                "english": "Download interrupted for {0}",
                "japanese": "{0} のダウンロードが中断されました",
                "korean": "{0}에 대한 다운로드가 중단됨",
                "chinese-simplified": "{0} 的下载已中断"
            },
            "error_downloading": {
                "english": "Error downloading {0}: {1}",
                "japanese": "{0} のダウンロード中にエラー: {1}",
                "korean": "{0} 다운로드 중 오류: {1}",
                "chinese-simplified": "下载 {0} 时出错: {1}"
            },
            "post_fully_downloaded": {
                "english": "Post {0} fully downloaded.",
                "japanese": "投稿 {0} が完全にダウンロードされました。",
                "korean": "게시물 {0}이(가) 완전히 다운로드되었습니다.",
                "chinese-simplified": "投稿 {0} 已完全下载。"
            },
            "all_files_downloaded": {
                "english": "All files for post {0} have been downloaded",
                "japanese": "投稿 {0} のすべてのファイルがダウンロードされました",
                "korean": "게시물 {0}의 모든 파일이 다운로드되었습니다",
                "chinese-simplified": "所有文件已下载完毕: {0}"
            },
            "no_files_selected_post": {
                "english": "No files selected for download for this post.",
                "japanese": "この投稿ではダウンロードするファイルが選択されていません。",
                "korean": "이 게시물에 대해 다운로드할 파일이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的文件。"
            },
            "language_changed": {
                "english": "Language changed to English",
                "japanese": "言語が日本語に変更されました",
                "korean": "언어가 한국어로 변경되었습니다",
                "chinese-simplified": "语言已更改为中文 (简体)"
            },
            # Media preview
            "media_preview": {
                "english": "Media Preview",
                "japanese": "メディアプレビュー",
                "korean": "미디어 미리보기",
                "chinese-simplified": "媒体预览"
            },
            "fit": {
                "english": "Fit",
                "japanese": "フィット",
                "korean": "맞춤",
                "chinese-simplified": "适合窗口"
            },
            "stretch": {
                "english": "Stretch",
                "japanese": "引き伸ばし",
                "korean": "늘이기",
                "chinese-simplified": "拉伸"
            },
            "original": {
                "english": "Original",
                "japanese": "オリジナル",
                "korean": "원본",
                "chinese-simplified": "原始大小"
            },
            "full_screen": {
                "english": "Full Screen (Modal)",
                "japanese": "全画面 (モーダル)",
                "korean": "전체 화면 (모달)",
                "chinese-simplified": "全屏 (模态)"
            },
            "audio_playback": {
                "english": "Audio Playback",
                "japanese": "オーディオ再生",
                "korean": "오디오 재생",
                "chinese-simplified": "音频播放"
            },
            "error_loading_media": {
                "english": "Error loading media",
                "japanese": "メディアの読み込みエラー",
                "korean": "미디어 로드 오류",
                "chinese-simplified": "加载媒体时出错"
            },
            # Error messages for media
            "invalid_url_format": {
                "english": "Invalid URL format. Expected: https://kemono.cr/[service]/user/[user_id]/post/[post_id]",
                "japanese": "無効なURL形式。期待される形式: https://kemono.cr/[service]/user/[user_id]/post/[post_id]",
                "korean": "잘못된 URL 형식. 예상 형식: https://kemono.cr/[service]/user/[user_id]/post/[post_id]",
                "chinese-simplified": "无效的 URL 格式。预期格式: https://kemono.cr/[service]/user/[user_id]/post/[post_id]"
            },
            "failed_to_fetch_post": {
                "english": "Failed to fetch post - Status code: {0}",
                "japanese": "投稿の取得に失敗しました - ステータスコード: {0}",
                "korean": "게시물 가져오기 실패 - 상태 코드: {0}",
                "chinese-simplified": "获取投稿失败 - 状态码: {0}"
            },
            "failed_to_fetch_post_error": {
                "english": "Failed to fetch post: {0}",
                "japanese": "投稿の取得に失敗しました: {0}",
                "korean": "게시물 가져오기 실패: {0}",
                "chinese-simplified": "获取投稿失败: {0}"
            },
            "no_valid_post_data": {
                "english": "No valid post data returned",
                "japanese": "有効な投稿データが返されませんでした",
                "korean": "유효한 게시물 데이터가 반환되지 않았습니다",
                "chinese-simplified": "未返回有效的投稿数据"
            },
            "invalid_image_data": {
                "english": "Invalid or corrupted image data",
                "japanese": "無効または破損した画像データ",
                "korean": "잘못되거나 손상된 이미지 데이터",
                "chinese-simplified": "无效或损坏的图像数据"
            },
            "failed_to_download": {
                "english": "Failed to download file from",
                "japanese": "ファイルのダウンロードに失敗しました",
                "korean": "파일 다운로드 실패",
                "chinese-simplified": "下载文件失败"
            },
            "unexpected_error": {
                "english": "Unexpected error while processing file from",
                "japanese": "ファイル処理中に予期しないエラーが発生しました",
                "korean": "파일 처리 중 예기치 않은 오류 발생",
                "chinese-simplified": "处理文件时发生意外错误"
            },
            "failed_to_load_gif": {
                "english": "Failed to load GIF from {0}: Invalid or corrupted GIF data",
                "japanese": "{0} からGIFを読み込めませんでした: 無効または破損したGIFデータ",
                "korean": "{0}에서 GIF 로드 실패: 잘못되거나 손상된 GIF 데이터",
                "chinese-simplified": "无法从 {0} 加载 GIF: 无效或损坏的 GIF 数据"
            },
            "no_internet_connection": {
                "english": "No internet connection. Update check failed.",
                "japanese": "インターネット接続がありません。更新チェックに失敗しました。",
                "korean": "인터넷 연결이 없습니다. 업데이트 확인 실패.",
                "chinese-simplified": "没有互联网连接。检查更新失败。"
            },
            "failed_to_check_updates": {
                "english": "Failed to check for updates",
                "japanese": "更新の確認に失敗しました",
                "korean": "업데이트 확인 실패",
                "chinese-simplified": "检查更新失败"
            },
            
            # Help Tab Translations (expanded with full content)
            "help_title": {
                "english": "Kemono Downloader User Manual",
                "japanese": "ケモノダウンローダーユーザーマニュアル",
                "korean": "케모노 다운로더 사용자 매뉴얼",
                "chinese-simplified": "Kemono 下载器用户手册"
            },
            "help_intro": {
                "english": "Welcome to the Kemono Downloader, a powerful tool designed to help you download content from Kemono.cr, "
                           "a platform that archives posts from various creator services such as Patreon, Fanbox, and more. This user manual provides "
                           "detailed instructions on how to use the application, covering every feature and tab in depth. Whether you're downloading a single post "
                           "or an entire creator's archive, this guide will walk you through each step, explain the interface, and offer troubleshooting tips to ensure a smooth experience.<br><br>"
                           "<b>Key Features:</b><br>"
                           "- Download individual posts or entire creator profiles from Kemono.cr.<br>"
                           "- Support for multiple file types including images (JPG, PNG, GIF), videos (MP4), archives (ZIP, 7Z), and PDFs.<br>"
                           "- Concurrent downloads for faster performance, with customizable settings.<br>"
                           "- Preview images before downloading to confirm content.<br>"
                           "- Deduplication of files using URL hashes to avoid redundant downloads.<br>"
                           "- Detailed logging for monitoring download progress and diagnosing issues.<br>"
                           "- Customizable save directories, themes, and notification settings.<br><br>"
                           "Follow the sections below to learn how to use each tab and feature of the Kemono Downloader.",
                "japanese": "ケモノダウンローダーへようこそ。このツールは、PatreonやFanboxなどのさまざまなクリエイターサービスから投稿をアーカイブするプラットフォーム、Kemono.suからコンテンツをダウンロードするために設計された強力なツールです。"
                           "このユーザーマニュアルでは、アプリケーションの使用方法を詳しく説明し、すべての機能とタブを深くカバーしています。単一の投稿をダウンロードする場合でも、クリエイター全体のアーカイブをダウンロードする場合でも、このガイドは各ステップを案内し、インターフェースを説明し、スムーズな体験を保証するためのトラブルシューティングのヒントを提供します。<br><br>"
                           "<b>主な機能:</b><br>"
                           "- Kemono.suから個々の投稿またはクリエイター全体のプロファイルをダウンロード。<br>"
                           "- 画像（JPG、PNG、GIF）、動画（MP4）、アーカイブ（ZIP、7Z）、PDFなど、複数のファイルタイプをサポート。<br>"
                           "- カスタマイズ可能な設定で、より高速なパフォーマンスのための同時ダウンロード。<br>"
                           "- ダウンロード前に画像をプレビューして内容を確認。<br>"
                           "- URLハッシュを使用してファイルの重複を回避。<br>"
                           "- ダウンロードの進捗状況の監視と問題の診断のための詳細なログ記録。<br>"
                           "- 保存ディレクトリ、テーマ、通知設定のカスタマイズ可能。<br><br>"
                           "以下のセクションに従って、ケモノダウンローダーの各タブと機能の使用方法を学んでください。",
                "korean": "케모노 다운로더에 오신 것을 환영합니다. 이 도구는 Patreon, Fanbox 등 다양한 크리에이터 서비스의 게시물을 아카이브하는 플랫폼인 Kemono.su에서 콘텐츠를 다운로드하도록 설계된 강력한 도구입니다. "
                          "이 사용자 매뉴얼은 애플리케이션 사용 방법에 대한 자세한 지침을 제공하며, 모든 기능과 탭을 심도 있게 다룹니다. 단일 게시물을 다운로드하든, 크리에이터 전체의 아카이브를 다운로드하든, 이 가이드는 각 단계를 안내하고 인터페이스를 설명하며 원활한 경험을 보장하기 위한 문제 해결 팁을 제공합니다.<br><br>"
                          "<b>주요 기능:</b><br>"
                          "- Kemono.su에서 개별 게시물 또는 전체 크리에이터 프로필을 다운로드.<br>"
                          "- 이미지(JPG, PNG, GIF), 비디오(MP4), 아카이브(ZIP, 7Z), PDF 등 다양한 파일 유형 지원.<br>"
                          "- 사용자 정의 가능한 설정으로 더 빠른 성능을 위한 동시 다운로드.<br>"
                          "- 다운로드 전에 이미지를 미리 보고 콘텐츠 확인.<br>"
                          "- URL 해시를 사용한 파일 중복 방지.<br>"
                          "- 다운로드 진행 상황 모니터링 및 문제 진단을 위한 상세 로그.<br>"
                          "- 저장 디렉토리, 테마, 알림 설정 사용자 정의 가능.<br><br>"
                          "아래 섹션을 따라 케모노 다운로더의 각 탭과 기능을 사용하는 방법을 알아보세요."
            },
            "help_getting_started_title": {
                "english": "1. Getting Started",
                "japanese": "1. はじめに",
                "korean": "1. 시작하기",
                "chinese-simplified": "1. 开始使用"
            },
            "help_getting_started_text": {
                "english": "<b>1.1 Launching the Application</b><br>"
                           "- When you first open the Kemono Downloader, you'll be greeted by an introductory screen featuring the application title 'Kemono.cr Downloader'.<br>"
                           "- Below the title, you'll see the developer's name ('Developed by VoxDroid') and a clickable link to the GitHub repository (github.com/VoxDroid) for updates and support.<br>"
                           "- Click the 'Launch' button in the center of the screen to proceed to the main interface.<br><br>"
                           "<b>1.2 Main Interface Overview</b><br>"
                           "The main interface is divided into four tabs, each serving a specific purpose:<br>"
                           "  - <b>Post Downloader</b>: Use this tab to download files from specific Kemono.cr posts by entering their URLs. Ideal for downloading individual posts.<br>"
                           "  - <b>Creator Downloader</b>: Use this tab to download content from an entire creator's profile, fetching all their posts and associated files.<br>"
                           "  - <b>Settings</b>: Configure the application's behavior, such as save directories, simultaneous downloads, and UI preferences.<br>"
                           "  - <b>Help</b>: You're here! This tab provides this comprehensive user manual to guide you through using the application.<br><br>"
                           "<b>1.3 Interface Elements</b><br>"
                           "- <b>Tabs</b>: Located at the top of the main interface, the tabs are styled with icons and labels. The active tab is highlighted with a darker background.<br>"
                           "- <b>Status Bar</b>: At the bottom of the window, a status label (e.g., 'Idle') indicates the application's current state. It updates during operations like downloading.<br>"
                           "- <b>Footer</b>: Also at the bottom, the footer displays the developer's name and GitHub link for quick access to the project page.<br><br>"
                           "<b>1.4 Initial Setup</b><br>"
                           "- Upon first launch, the application creates several directories in the default save location (configurable in the Settings tab):<br>"
                           "  - <b>Downloads</b>: Where downloaded files are saved.<br>"
                           "  - <b>Cache</b>: Stores temporary files for image previews.<br>"
                           "  - <b>Other Files</b>: Contains metadata like file hashes for deduplication.<br>"
                           "- Ensure you have an active internet connection, as the application needs to fetch data from Kemono.cr.",
                "japanese": "<b>1.1 アプリケーションの起動</b><br>"
                            "- ケモノダウンローダーを初めて開くと、アプリケーションタイトル「Kemono.cr Downloader」が表示された紹介画面が表示されます。<br>"
                            "- タイトルの下には、開発者名（「Developed by VoxDroid」）と、更新やサポートのためのGitHubリポジトリへのクリック可能なリンク（github.com/VoxDroid）が表示されます。<br>"
                            "- 画面中央の「起動」ボタンをクリックしてメインインターフェースに進みます。<br><br>"
                            "<b>1.2 メインインターフェースの概要</b><br>"
                            "メインインターフェースは4つのタブに分かれており、それぞれ特定の目的を持っています：<br>"
                            "  - <b>投稿ダウンローダー</b>：このタブを使用して、URLを入力することで特定のKemono.su投稿からファイルをダウンロードします。個々の投稿のダウンロードに最適です。<br>"
                            "  - <b>クリエイターダウンローダー</b>：このタブを使用して、クリエイター全体のプロフィールからコンテンツをダウンロードし、すべての投稿と関連ファイルをフェッチします。<br>"
                            "  - <b>設定</b>：保存ディレクトリ、同時ダウンロード数、UI設定など、アプリケーションの動作を設定します。<br>"
                            "  - <b>ヘルプ</b>：ここです！このタブは、アプリケーションの使用をガイドする包括的なユーザーマニュアルを提供します。<br><br>"
                            "<b>1.3 インターフェース要素</b><br>"
                            "- <b>タブ</b>：メインインターフェースの上部に位置し、アイコンとラベルでスタイルされています。アクティブなタブは濃い背景で強調されます。<br>"
                            "- <b>ステータスバー</b>：ウィンドウの下部にあり、ステータスラベル（例：「アイドル」）がアプリケーションの現在の状態を示します。ダウンロードなどの操作中に更新されます。<br>"
                            "- <b>フッター</b>：下部にもあり、開発者名とGitHubリンクが表示され、プロジェクトページに素早くアクセスできます。<br><br>"
                            "<b>1.4 初期設定</b><br>"
                            "- 初回起動時に、アプリケーションはデフォルトの保存場所（設定タブで変更可能）にいくつかのディレクトリを作成します：<br>"
                            "  - <b>ダウンロード</b>：ダウンロードしたファイルが保存される場所。<br>"
                            "  - <b>キャッシュ</b>：画像プレビューの一時ファイルを保存します。<br>"
                            "  - <b>その他のファイル</b>：重複排除のためのファイルハッシュなどのメタデータを含みます。<br>"
                            "- アプリケーションはKemono.suからデータをフェッチする必要があるため、アクティブなインターネット接続を確保してください。",
                "korean": "<b>1.1 애플리케이션 실행</b><br>"
                          "- 케모노 다운로더를 처음 열면 'Kemono.cr Downloader'라는 애플리케이션 제목이 포함된 소개 화면이 표시됩니다。<br>"
                          "- 제목 아래에는 개발자 이름('Developed by VoxDroid')과 업데이트 및 지원을 위한 GitHub 저장소에 대한 클릭 가능한 링크(github.com/VoxDroid)가 표시됩니다.<br>"
                          "- 화면 중앙의 '실행' 버튼을 클릭하여 메인 인터페이스로 이동합니다。<br><br>"
                          "<b>1.2 메인 인터페이스 개요</b><br>"
                          "메인 인터페이스는 네 개의 탭으로 나뉘며, 각 탭은 특정 목적을 제공합니다:<br>"
                          "  - <b>게시물 다운로더</b>: 이 탭을 사용하여 URL을 입력함으로써 특정 Kemono.cr 게시물에서 파일을 다운로드합니다. 개별 게시물 다운로드에 이상적입니다.<br>"
                          "  - <b>크리에이터 다운로더</b>: 이 탭을 사용하여 크리에이터 전체 프로필에서 콘텐츠를 다운로드하며, 모든 게시물과 관련 파일을 가져옵니다.<br>"
                          "  - <b>설정</b>: 저장 디렉토리, 동시 다운로드 수, UI 설정 등 애플리케이션 동작을 구성합니다.<br>"
                          "  - <b>도움말</b>: 여기입니다! 이 탭은 애플리케이션 사용을 안내하는 포괄적인 사용자 매뉴얼을 제공합니다.<br><br>"
                          "<b>1.3 인터페이스 요소</b><br>"
                          "- <b>탭</b>: 메인 인터페이스 상단에 위치하며, 아이콘과 레이블로 스타일이 지정됩니다. 활성 탭은 더 어두운 배경으로 강조됩니다.<br>"
                          "- <b>상태 표시줄</b>: 창 하단에 있으며, 상태 레이블(예: '대기 중')이 애플리케이션의 현재 상태를 나타냅니다. 다운로드와 같은 작업 중에 업데이트됩니다.<br>"
                          "- <b>푸터</b>: 하단에도 있으며, 개발자 이름과 GitHub 링크가 표시되어 프로젝트 페이지에 빠르게 접근할 수 있습니다.<br><br>"
                          "<b>1.4 초기 설정</b><br>"
                          "- 첫 실행 시, 애플리케이션은 기본 저장 위치(설정 탭에서 변경 가능)에 여러 디렉토리를 생성합니다:<br>"
                          "  - <b>다운로드</b>: 다운로드된 파일이 저장되는 곳입니다.<br>"
                          "  - <b>캐시</b>: 이미지 미리보기를 위한 임시 파일을 저장합니다.<br>"
                          "  - <b>기타 파일</b>: 중복 제거를 위한 파일 해시와 같은 메타데이터를 포함합니다.<br>"
                          "- 애플리케이션이 Kemono.su에서 데이터를 가져와야 하므로 활성 인터넷 연결을 확인하세요."
            },
            "help_post_downloader_title": {
                "english": "2. Using the Post Downloader Tab",
                "japanese": "2. 投稿ダウンローダータブの使用",
                "korean": "2. 게시물 다운로더 탭 사용",
                "chinese-simplified": "2. 使用投稿下载器选项卡"
            },
            "help_post_downloader_text": {
                "english": "The Post Downloader tab is designed for downloading content from specific Kemono.cr posts. You can add multiple posts to a queue, view their contents, select files to download, and monitor the download progress. Below are the detailed steps to use this tab effectively:<br><br>"
                           "<b>2.1 Adding a Post to the Queue</b><br>"
                           "- <b>Step 1</b>: Navigate to the 'Post Downloader' tab by clicking its label at the top of the interface. The tab is marked with a download icon.<br>"
                           "- <b>Step 2</b>: Locate the 'Enter post URL' field at the top left of the tab. This is a text input field with a placeholder text 'Enter post URL (e.g., https://kemono.cr/patreon/user/123/post/456)'.<br>"
                           "- <b>Step 3</b>: Enter the URL of a Kemono.cr post. The URL must follow the format: https://kemono.cr/[service]/user/[user_id]/post/[post_id]. For example: https://kemono.cr/patreon/user/123456785/post/12345678.<br>"
                           "- <b>Step 4</b>: Click the 'Add to Queue' button next to the input field. The button is styled with a plus icon and a blue background.<br>"
                           "- <b>Step 5</b>: The post URL will appear in the 'Post Queue' list below the input field. Each entry in the list includes:<br>"
                           "  - An eye icon to view the post's contents.<br>"
                           "  - The post URL as a clickable label.<br>"
                           "  - An 'X' button to remove the post from the queue.<br><br>"
                           "<b>2.2 Viewing Post Contents</b><br>"
                           "- <b>Step 1</b>: In the 'Post Queue' list, find the post you want to inspect.<br>"
                           "- <b>Step 2</b>: Click the eye icon next to the post URL. This initiates a background task to fetch the post's data from Kemono.cr.<br>"
                           "- <b>Step 3</b>: The files associated with the post will be displayed in the 'Files to Download' list on the right side of the tab.<br>"
                           "- <b>Step 4</b>: Use the 'Filter by Type' checkboxes (e.g., JPG, ZIP, MP4) to show only specific file types. For example, checking 'JPG' will display only image files with .jpg or .jpeg extensions.<br>"
                           "- <b>Step 5</b>: Use the search bar above the 'Files to Download' list to filter files by name. For example, typing 'image' will show only files with 'image' in their names.<br>"
                           "- <b>Note</b>: The 'Background Task Progress' bar at the bottom right will show a looping animation while the post data is being fetched. The label above it will read 'Fetching files from link...'.<br><br>"
                           "<b>2.3 Selecting Files to Download</b><br>"
                           "- <b>Step 1</b>: In the 'Files to Download' list, each file is listed with a checkbox next to its name. By default, all files are selected (checkboxes are checked).<br>"
                           "- <b>Step 2</b>: Uncheck the boxes next to files you do not wish to download. For example, if you only want images, uncheck ZIP or MP4 files.<br>"
                           "- <b>Step 3</b>: Use the 'Check ALL' checkbox above the list to quickly select or deselect all visible files. If filters are applied, this affects only the filtered files.<br>"
                           "- <b>Step 4</b>: To download files from all posts in the queue at once, check the 'Download All Links' option. This disables individual file selection and prepares all files from all queued posts for download.<br>"
                           "- <b>Note</b>: When 'Download All Links' is enabled, the checkboxes in the 'Files to Download' list are disabled, and the application will attempt to download all files from all posts in the queue.<br><br>"
                           "<b>2.4 Starting the Download</b><br>"
                           "- <b>Step 1</b>: Ensure you have selected the desired files or enabled 'Download All Links'.<br>"
                           "- <b>Step 2</b>: Click the 'Download' button at the bottom left of the tab. The button is marked with a download icon and styled with a blue background.<br>"
                           "- <b>Step 3</b>: The download process will begin, and the following elements will update:<br>"
                           "  - <b>File Progress Bar</b>: Shows the progress of the current file being downloaded (0% to 100%). The label above it (e.g., 'File Progress 50%') updates accordingly.<br>"
                           "  - <b>Overall Progress Bar</b>: Displays the total progress across all files and posts (e.g., 'Overall Progress (5/10 files, 2/3 posts)').<br>"
                           "  - <b>Console</b>: Logs messages about the download process, such as 'Starting download of file 1/10: [URL]' or 'Successfully downloaded: [path]'. Logs are color-coded: green for info, yellow for warnings, red for errors.<br>"
                           "- <b>Note</b>: During the download, the 'Download' button becomes disabled, and the 'Cancel' button is enabled.<br><br>"
                           "<b>2.5 Managing Downloads</b><br>"
                           "- <b>Canceling Downloads</b>: Click the 'Cancel' button (marked with an 'X' icon) to stop all active downloads. The progress bars will turn yellow, and the labels will update to 'Downloads Terminated'.<br>"
                           "- <b>Removing Posts from Queue</b>: Click the 'X' button next to a post URL in the 'Post Queue' list to remove it. You'll be prompted to confirm the removal.<br>"
                           "- <b>Previewing Images</b>: Select an image file (JPG, JPEG, PNG, or GIF) in the 'Files to Download' list, then click the eye icon button below the list to preview it. A modal window will open showing the image, with a progress bar while it loads.<br>"
                           "- <b>Note</b>: If a post is removed during an active download, the download for that post's files will be canceled.<br><br>"
                           "<b>2.6 Where Files Are Saved</b><br>"
                           "- Files are saved in the directory specified in the Settings tab (default is your user directory under 'Kemono Downloader/Downloads').<br>"
                           "- The folder structure is organized as follows:<br>"
                           "  - <b>Service Folder</b>: Named after the service (e.g., 'patreon').<br>"
                           "  - <b>Post Folder</b>: Named 'post_[post_id]' (e.g., 'post_12345678').<br>"
                           "  - Example: If downloading from https://kemono.cr/patreon/user/123456785/post/12345678, files will be saved in '[Save Directory]/patreon/post_12345678/'.<br>"
                           "- Files are named based on their original URLs, with any special characters (e.g., '/') replaced with underscores to ensure compatibility with your filesystem.<br><br>"
                           "<b>2.7 Additional Features</b><br>"
                           "- <b>Concurrent Downloads</b>: The application supports downloading multiple files simultaneously, with the number of concurrent downloads set in the Settings tab (default is 10, adjustable between 1-10).<br>"
                           "- <b>File Deduplication</b>: The application uses URL hashes to detect and skip previously downloaded files, preventing duplicates. Hash data is stored in the 'Other Files' directory as 'file_hashes.json'.<br>"
                           "- <b>Image Caching</b>: When previewing images, they are cached in the 'Cache' directory to speed up future previews of the same image.<br>"
                           "- <b>Logging</b>: The console provides detailed logs of all operations, including file detection, download progress, and errors. This is useful for debugging issues.",
                "japanese": "投稿ダウンローダータブは、特定のKemono.su投稿からコンテンツをダウンロードするために設計されています。複数の投稿をキューに追加し、その内容を表示し、ダウンロードするファイルを選択し、ダウンロードの進捗を監視できます。以下に、このタブを効果的に使用するための詳細な手順を示します：<br><br>"
                            "<b>2.1 投稿をキューに追加する</b><br>"
                            "- <b>ステップ1</b>：インターフェース上部の「投稿ダウンローダー」タブをクリックして移動します。このタブはダウンロードアイコンでマークされています。<br>"
                            "- <b>ステップ2</b>：タブの左上にある「投稿URLを入力」フィールドを見つけます。これは「投稿URLを入力（例: https://kemono.cr/patreon/user/123/post/456）」というプレースホルダーテキストが表示されたテキスト入力フィールドです。<br>"
                            "- <b>ステップ3</b>：Kemono.suの投稿URLを入力します。URLは次の形式である必要があります：https://kemono.cr/[service]/user/[user_id]/post/[post_id]。例: https://kemono.cr/patreon/user/123456785/post/12345678。<br>"
                            "- <b>ステップ4</b>：入力フィールドの横にある「キューに追加」ボタンをクリックします。このボタンはプラスアイコンと青い背景でスタイルされています。<br>"
                            "- <b>ステップ5</b>：投稿URLが入力フィールド下の「投稿キュー」リストに表示されます。リストの各エントリには以下が含まれます：<br>"
                            "  - 投稿の内容を表示するための目アイコン。<br>"
                            "  - クリック可能なラベルとしての投稿URL。<br>"
                            "  - キューから投稿を削除するための「X」ボタン。<br><br>"
                            "<b>2.2 投稿内容の表示</b><br>"
                            "- <b>ステップ1</b>：「投稿キュー」リストで、確認したい投稿を見つけます。<br>"
                            "- <b>ステップ2</b>：投稿URLの横にある目アイコンをクリックします。これにより、Kemono.suから投稿データを取得するバックグラウンドタスクが開始されます。<br>"
                            "- <b>ステップ3</b>：投稿に関連するファイルがタブの右側にある「ダウンロードするファイル」リストに表示されます。<br>"
                            "- <b>ステップ4</b>：「タイプでフィルタリング」チェックボックス（例: JPG、ZIP、MP4）を使用して、特定のファイルタイプのみを表示します。たとえば、「JPG」をチェックすると、.jpgまたは.jpeg拡張子の画像ファイルのみが表示されます。<br>"
                            "- <b>ステップ5</b>：「ダウンロードするファイル」リスト上部の検索バーを使用して、名前でファイルをフィルタリングします。たとえば、「image」と入力すると、「image」という名前を含むファイルのみが表示されます。<br>"
                            "- <b>注意</b>：投稿データが取得されている間、右下の「バックグラウンドタスク進捗」バーがループアニメーションを表示し、その上のラベルには「リンクからファイルをフェッチ中...」と表示されます。<br><br>"
                            "<b>2.3 ダウンロードするファイルの選択</b><br>"
                            "- <b>ステップ1</b>：「ダウンロードするファイル」リストでは、各ファイルが名前横のチェックボックスと共にリストされています。デフォルトではすべてのファイルが選択されています（チェックボックスがオン）。<br>"
                            "- <b>ステップ2</b>：ダウンロードしたくないファイルのチェックボックスをオフにします。たとえば、画像だけが必要な場合、ZIPやMP4ファイルのチェックを外します。<br>"
                            "- <b>ステップ3</b>：リスト上部の「すべてチェック」チェックボックスを使用して、表示されているすべてのファイルを迅速に選択または選択解除します。フィルターが適用されている場合、これはフィルターされたファイルにのみ影響します。<br>"
                            "- <b>ステップ4</b>：キュー内のすべての投稿から一度にファイルをダウンロードするには、「すべてのリンクをダウンロード」オプションをチェックします。これにより個別のファイル選択が無効になり、キュー内のすべての投稿からすべてのファイルがダウンロードの準備をします。<br>"
                            "- <b>注意</b>：「すべてのリンクをダウンロード」が有効な場合、「ダウンロードするファイル」リストのチェックボックスが無効になり、アプリケーションはキュー内のすべての投稿からすべてのファイルをダウンロードしようとします。<br><br>"
                            "<b>2.4 ダウンロードの開始</b><br>"
                            "- <b>ステップ1</b>：希望するファイルを選択したか、「すべてのリンクをダウンロード」を有効にしたことを確認します。<br>"
                            "- <b>ステップ2</b>：タブの左下にある「ダウンロード」ボタンをクリックします。このボタンはダウンロードアイコンでマークされ、青い背景でスタイルされています。<br>"
                            "- <b>ステップ3</b>：ダウンロードプロセスが開始され、以下の要素が更新されます：<br>"
                            "  - <b>ファイル進捗バー</b>：現在ダウンロード中のファイルの進捗（0%から100%）を表示します。その上のラベル（例: 「ファイル進捗 50%」）がそれに応じて更新されます。<br>"
                            "  - <b>全体進捗バー</b>：すべてのファイルと投稿にわたる全体の進捗を表示します（例: 「全体進捗 (5/10 ファイル, 2/3 投稿)」）。<br>"
                            "  - <b>コンソール</b>：ダウンロードプロセスに関するメッセージを記録します。たとえば、「ファイル 1/10 のダウンロード開始: [URL]」や「ダウンロード成功: [path]」など。ログは色分けされています：情報は緑、警告は黄、エラーは赤。<br>"
                            "- <b>注意</b>：ダウンロード中は「ダウンロード」ボタンが無効になり、「キャンセル」ボタンが有効になります。<br><br>"
                            "<b>2.5 ダウンロードの管理</b><br>"
                            "- <b>ダウンロードのキャンセル</b>：「キャンセル」ボタン（「X」アイコンでマーク）をクリックしてすべてのアクティブなダウンロードを停止します。進捗バーが黄色に変わり、ラベルが「ダウンロード中断」に更新されます。<br>"
                            "- <b>キューからの投稿の削除</b>：「投稿キュー」リストの投稿URL横の「X」ボタンをクリックして削除します。削除の確認が求められます。<br>"
                            "- <b>画像のプレビュー</b>：「ダウンロードするファイル」リストで画像ファイル（JPG、JPEG、PNG、またはGIF）を選択し、リスト下の目アイコンボタンをクリックしてプレビューします。画像を表示するモーダルウィンドウが開き、読み込み中に進捗バーが表示されます。<br>"
                            "- <b>注意</b>：アクティブなダウンロード中に投稿が削除された場合、その投稿のファイルのダウンロードがキャンセルされます。<br><br>"
                            "<b>2.6 ファイルの保存場所</b><br>"
                            "- ファイルは設定タブで指定されたディレクトリに保存されます（デフォルトはユーザーディレクトリ内の「Kemono Downloader/Downloads」）。<br>"
                            "- フォルダ構造は次のように整理されています：<br>"
                            "  - <b>サービスフォルダ</b>：サービス名に基づいて命名されます（例: 「patreon」）。<br>"
                            "  - <b>投稿フォルダ</b>：「post_[post_id]」と命名されます（例: 「post_12345678」）。<br>"
                            "  - 例: https://kemono.cr/patreon/user/123456785/post/12345678 からダウンロードする場合、ファイルは「[保存ディレクトリ]/patreon/post_12345678/」に保存されます。<br>"
                            "- ファイル名は元のURLに基づいて命名され、ファイルシステムとの互換性を確保するために特殊文字（例: 「/」）はアンダースコアに置き換えられます。<br><br>"
                            "<b>2.7 追加機能</b><br>"
                            "- <b>同時ダウンロード</b>：アプリケーションは複数のファイルを同時にダウンロードでき、同時ダウンロードの数は設定タブで設定されます（デフォルトは10、1-10の間で調整可能）。<br>"
                            "- <b>ファイルの重複排除</b>：アプリケーションはURLハッシュを使用して以前にダウンロードされたファイルを検出し、重複を防ぎます。ハッシュデータは「その他のファイル」ディレクトリ内の「file_hashes.json」に保存されます。<br>"
                            "- <b>画像キャッシュ</b>：画像をプレビューする際、それらは「キャッシュ」ディレクトリにキャッシュされ、同じ画像の将来のプレビューを高速化します。<br>"
                            "- <b>ログ記録</b>：コンソールは、ファイル検出、ダウンロード進捗、エラーを含むすべての操作の詳細なログを提供し、問題のデバッグに役立ちます。",
                "korean": "게시물 다운로더 탭은 특정 Kemono.cr 게시물에서 콘텐츠를 다운로드하기 위해 설계되었습니다. 여러 게시물을 대기열에 추가하고, 내용을 보고, 다운로드할 파일을 선택하며, 다운로드 진행 상황을 모니터링할 수 있습니다. 아래는 이 탭을 효과적으로 사용하는 자세한 단계입니다:<br><br>"
                          "<b>2.1 게시물을 대기열에 추가하기</b><br>"
                          "- <b>단계 1</b>: 인터페이스 상단의 '게시물 다운로더' 탭을 클릭하여 이동합니다. 이 탭은 다운로드 아이콘으로 표시됩니다.<br>"
                          "- <b>단계 2</b>: 탭의 좌측 상단에 있는 '게시물 URL 입력' 필드를 찾습니다. 이 필드는 '게시물 URL 입력(예: https://kemono.cr/patreon/user/123/post/456)'이라는 플레이스홀더 텍스트가 있는 텍스트 입력 필드입니다.<br>"
                          "- <b>단계 3</b>: Kemono.cr 게시물의 URL을 입력합니다. URL은 다음 형식을 따라야 합니다: https://kemono.cr/[service]/user/[user_id]/post/[post_id]. 예: https://kemono.cr/patreon/user/123456785/post/12345678.<br>"
                          "- <b>단계 4</b>: 입력 필드 옆의 '대기열에 추가' 버튼을 클릭합니다. 이 버튼은 플러스 아이콘과 파란색 배경으로 스타일링되어 있습니다.<br>"
                          "- <b>단계 5</b>: 게시물 URL이 입력 필드 아래의 '게시물 대기열' 목록에 나타납니다. 목록의 각 항목에는 다음이 포함됩니다:<br>"
                          "  - 게시물 내용을 보기 위한 눈 아이콘.<br>"
                          "  - 클릭 가능한 레이블로 표시된 게시물 URL.<br>"
                          "  - 대기열에서 게시물을 제거하기 위한 'X' 버튼.<br><br>"
                          "<b>2.2 게시물 내용 보기</b><br>"
                          "- <b>단계 1</b>: '게시물 대기열' 목록에서 확인하고 싶은 게시물을 찾습니다.<br>"
                          "- <b>단계 2</b>: 게시물 URL 옆의 눈 아이콘을 클릭합니다. 그러면 Kemono.su에서 게시물 데이터를 가져오는 백그라운드 작업이 시작됩니다.<br>"
                          "- <b>단계 3</b>: 게시물과 관련된 파일이 탭의 오른쪽에 있는 '다운로드할 파일' 목록에 표시됩니다.<br>"
                          "- <b>단계 4</b>: '유형별 필터링' 체크박스(예: JPG, ZIP, MP4)를 사용하여 특정 파일 유형만 표시합니다. 예를 들어, 'JPG'를 체크하면 .jpg 또는 .jpeg 확장자를 가진 이미지 파일만 표시됩니다.<br>"
                          "- <b>단계 5</b>: '다운로드할 파일' 목록 위의 검색창을 사용하여 파일 이름을 필터링합니다. 예를 들어, 'image'를 입력하면 이름에 'image'가 포함된 파일만 표시됩니다.<br>"
                          "- <b>참고</b>: 게시물 데이터가 가져와지는 동안 오른쪽 하단의 '백그라운드 작업 진행률' 바가 루프 애니메이션을 표시하며, 위의 레이블은 '링크에서 파일 가져오는 중...'이라고 표시됩니다.<br><br>"
                          "<b>2.3 다운로드할 파일 선택</b><br>"
                          "- <b>단계 1</b>: '다운로드할 파일' 목록에서 각 파일은 이름 옆에 체크박스와 함께 나열됩니다. 기본적으로 모든 파일이 선택되어 있습니다(체크박스가 체크됨).<br>"
                          "- <b>단계 2</b>: 다운로드하고 싶지 않은 파일의 체크박스를 해제합니다. 예를 들어, 이미지 파일만 원한다면 ZIP이나 MP4 파일의 체크를 해제합니다.<br>"
                          "- <b>단계 3</b>: 목록 위의 '모두 선택' 체크박스를 사용하여 표시된 모든 파일을 빠르게 선택하거나 선택 해제합니다. 필터가 적용된 경우, 이는 필터링된 파일에만 영향을 미칩니다.<br>"
                          "- <b>단계 4</b>: 대기열에 있는 모든 게시물의 파일을 한 번에 다운로드하려면 '모든 링크 다운로드' 옵션을 체크합니다. 이렇게 하면 개별 파일 선택이 비활성화되고 대기열에 있는 모든 게시물의 모든 파일이 다운로드 준비됩니다.<br>"
                          "- <b>참고</b>: '모든 링크 다운로드'가 활성화되면 '다운로드할 파일' 목록의 체크박스가 비활성화되며, 애플리케이션은 대기열에 있는 모든 게시물의 모든 파일을 다운로드하려고 시도합니다.<br><br>"
                          "<b>2.4 다운로드 시작</b><br>"
                          "- <b>단계 1</b>: 원하는 파일을 선택했거나 '모든 링크 다운로드'를 활성화했는지 확인합니다.<br>"
                          "- <b>단계 2</b>: 탭의 좌측 하단에 있는 '다운로드' 버튼을 클릭합니다. 이 버튼은 다운로드 아이콘으로 표시되며 파란색 배경으로 스타일링되어 있습니다.<br>"
                          "- <b>단계 3</b>: 다운로드 프로세스가 시작되며, 다음 요소들이 업데이트됩니다:<br>"
                          "  - <b>파일 진행률 바</b>: 현재 다운로드 중인 파일의 진행률(0%에서 100%)을 표시합니다. 위의 레이블(예: '파일 진행률 50%')이 그에 따라 업데이트됩니다.<br>"
                          "  - <b>전체 진행률 바</b>: 모든 파일과 게시물에 걸친 총 진행률을 표시합니다(예: '전체 진행률 (5/10 파일, 2/3 게시물)').<br>"
                          "  - <b>콘솔</b>: 다운로드 프로세스에 대한 메시지를 기록합니다. 예: '파일 1/10 다운로드 시작: [URL]' 또는 '다운로드 성공: [경로]'. 로그는 색상으로 구분됩니다: 정보는 녹색, 경고는 노란색, 오류는 빨간색.<br>"
                          "- <b>참고</b>: 다운로드 중에는 '다운로드' 버튼이 비활성화되고 '취소' 버튼이 활성화됩니다.<br><br>"
                          "<b>2.5 다운로드 관리</b><br>"
                          "- <b>다운로드 취소</b>: '취소' 버튼('X' 아이콘으로 표시)을 클릭하여 모든 활성 다운로드를 중지합니다. 진행률 바가 노란색으로 변하고 레이블이 '다운로드 중단됨'으로 업데이트됩니다.<br>"
                          "- <b>대기열에서 게시물 제거</b>: '게시물 대기열' 목록에서 게시물 URL 옆의 'X' 버튼을 클릭하여 제거합니다. 제거 확인 메시지가 표시됩니다.<br>"
                          "- <b>이미지 미리보기</b>: '다운로드할 파일' 목록에서 이미지 파일(JPG, JPEG, PNG, GIF)을 선택한 후 목록 아래의 눈 아이콘 버튼을 클릭하여 미리 봅니다. 이미지를 표시하는 모달 창이 열리며, 로드 중에는 진행률 바가 표시됩니다.<br>"
                          "- <b>참고</b>: 활성 다운로드 중에 게시물이 제거되면 해당 게시물의 파일 다운로드가 취소됩니다.<br><br>"
                          "<b>2.6 파일 저장 위치</b><br>"
                          "- 파일은 설정 탭에서 지정된 디렉토리에 저장됩니다(기본값은 사용자 디렉토리 내 'Kemono Downloader/Downloads').<br>"
                          "- 폴더 구조는 다음과 같이 구성됩니다:<br>"
                          "  - <b>서비스 폴더</b>: 서비스 이름으로 명명됩니다(예: 'patreon').<br>"
                          "  - <b>게시물 폴더</b>: 'post_[post_id]'로 명명됩니다(예: 'post_12345678').<br>"
                          "  - 예: https://kemono.cr/patreon/user/123456785/post/12345678에서 다운로드하면 파일은 '[저장 디렉토리]/patreon/post_12345678/'에 저장됩니다.<br>"
                          "- 파일 이름은 원래 URL을 기반으로 하며, 파일 시스템 호환성을 보장하기 위해 특수 문자(예: '/')는 밑줄로 대체됩니다.<br><br>"
                          "<b>2.7 추가 기능</b><br>"
                          "- <b>동시 다운로드</b>: 애플리케이션은 여러 파일을 동시에 다운로드할 수 있으며, 동시 다운로드 수는 설정 탭에서 설정됩니다(기본값은 10, 1-10 사이에서 조정 가능).<br>"
                          "- <b>파일 중복 제거</b>: 애플리케이션은 URL 해시를 사용하여 이전에 다운로드된 파일을 감지하고 중복을 방지합니다. 해시 데이터는 '기타 파일' 디렉토리의 'file_hashes.json'에 저장됩니다.<br>"
                          "- <b>이미지 캐싱</b>: 이미지를 미리 볼 때, '캐시' 디렉토리에 캐시되어 동일한 이미지의 향후 미리보기를 빠르게 합니다.<br>"
                          "- <b>로깅</b>: 콘솔은 파일 감지, 다운로드 진행 상황, 오류를 포함한 모든 작업에 대한 자세한 로그를 제공하여 문제 디버깅에 유용합니다."
            },
            "help_creator_downloader_title": {
                "english": "3. Using the Creator Downloader Tab",
                "japanese": "3. クリエイターダウンローダータブの使用",
                "korean": "3. 크리에이터 다운로더 탭 사용",
                "chinese-simplified": "3. 使用创作者下载器选项卡"
            },
            "help_creator_downloader_text": {
                "english": "The Creator Downloader tab is designed for bulk downloading content from a creator's entire profile on Kemono.cr. You can queue multiple creators, fetch their posts, select specific content to download, and monitor the progress. This tab is ideal for archiving a creator's work or downloading content from multiple creators at once. Below are the detailed steps to use this tab effectively:<br><br>"
                           "<b>3.1 Adding a Creator to the Queue</b><br>"
                           "- <b>Step 1</b>: Navigate to the 'Creator Downloader' tab by clicking its label at the top of the interface. The tab is marked with a user-edit icon.<br>"
                           "- <b>Step 2</b>: Locate the 'Enter creator URL' field at the top left of the tab. This is a text input field with a placeholder text 'Enter creator URL (e.g., https://kemono.cr/patreon/user/12345678)'.<br>"
                           "- <b>Step 3</b>: Enter the URL of a creator's profile on Kemono.cr. The URL must follow the format: https://kemono.cr/[service]/user/[user_id]. For example: https://kemono.cr/patreon/user/12345678.<br>"
                           "- <b>Step 4</b>: Click the 'Add to Queue' button next to the input field. The button is styled with a plus icon and a blue background.<br>"
                           "- <b>Step 5</b>: The creator URL will appear in the 'Creator Queue' list below the input field. Each entry in the list includes:<br>"
                           "  - An eye icon to fetch and view the creator's posts.<br>"
                           "  - The creator URL as a clickable label.<br>"
                           "  - An 'X' button to remove the creator from the queue.<br>"
                           "- <b>Note</b>: Duplicate URLs are automatically prevented. If you try to add a URL already in the queue, a warning message will appear in the console: '[WARNING] URL already in queue.'<br><br>"
                           "<b>3.2 Viewing Creator Posts</b><br>"
                           "- <b>Step 1</b>: In the 'Creator Queue' list, find the creator whose posts you want to view.<br>"
                           "- <b>Step 2</b>: Click the eye icon next to the creator URL. This initiates a background task to fetch all posts associated with the creator from Kemono.cr.<br>"
                           "- <b>Step 3</b>: The posts will be displayed in the 'Posts to Download' list on the right side of the tab. Each post entry includes:<br>"
                           "  - A checkbox to select the post for download.<br>"
                           "  - The post title (or 'Post [post_id]' if no title is available).<br>"
                           "  - A thumbnail URL (if available) stored as user data for previewing.<br>"
                           "- <b>Step 4</b>: Use the search bar above the 'Posts to Download' list to filter posts by title. For example, typing 'artwork' will show only posts with 'artwork' in their titles.<br>"
                           "- <b>Note</b>: The 'Background Task Progress' bar at the bottom right will show a looping animation while posts are being fetched, with the label 'Detecting posts from link...'. Once complete, the label changes to 'Idle'.<br><br>"
                           "<b>3.3 Configuring Download Options</b><br>"
                           "- <b>Step 1</b>: Under the 'Download Options' group box, configure which content types to include in the download:<br>"
                           "  - <b>Main File</b>: Includes the primary file attached to each post (e.g., a featured image or video). Enabled by default.<br>"
                           "  - <b>Attachments</b>: Includes additional files attached to the post (e.g., ZIP files, extra images). Enabled by default.<br>"
                           "  - <b>Content Images</b>: Includes images embedded in the post's content (e.g., images in the post description). Enabled by default.<br>"
                           "- <b>Step 2</b>: In the 'File Extensions' group box, select which file types to download:<br>"
                           "  - Options include JPG/JPEG, PNG, ZIP, MP4, GIF, PDF, and 7Z.<br>"
                           "  - All file types are enabled by default. Uncheck any file types you do not wish to download.<br>"
                           "  - Example: If you only want images, uncheck ZIP, MP4, PDF, and 7Z, leaving JPG/JPEG, PNG, and GIF checked.<br>"
                           "- <b>Note</b>: Changing these options will automatically update the list of files to download when you start the download process.<br><br>"
                           "<b>3.4 Selecting Posts to Download</b><br>"
                           "- <b>Step 1</b>: In the 'Posts to Download' list, check the boxes next to the posts you want to download. By default, no posts are selected.<br>"
                           "- <b>Step 2</b>: Use the 'Check ALL' checkbox above the list to select or deselect all visible posts. If the search filter is applied, this affects only the filtered posts.<br>"
                           "- <b>Step 3</b>: Alternatively, enable the 'Download All Links' option to download all files from all queued creators without manual selection:<br>"
                           "  - When enabled, this option disables individual post checkboxes and fetches all posts from all creators in the queue.<br>"
                           "  - The application will automatically select all posts for download, ignoring manual selections.<br>"
                           "- <b>Note</b>: The 'Posts: [number]' label below the list updates to reflect the number of selected posts. When 'Download All Links' is enabled, this shows the total number of posts across all queued creators.<br><br>"
                           "<b>3.5 Starting the Download</b><br>"
                           "- <b>Step 1</b>: Ensure you have selected the desired posts or enabled 'Download All Links'.<br>"
                           "- <b>Step 2</b>: Click the 'Download' button at the bottom left of the tab. The button is marked with a download icon and styled with a blue background.<br>"
                           "- <b>Step 3</b>: The application will first prepare the files for download, showing 'Preparing files to download...' in the background task label and a progress bar.<br>"
                           "- <b>Step 4</b>: Once preparation is complete, the download process begins, and the following elements update:<br>"
                           "  - <b>File Progress Bar</b>: Shows the progress of the current file being downloaded (0% to 100%). The label above it (e.g., 'File Progress 50%') updates accordingly.<br>"
                           "  - <b>Overall Progress Bar</b>: Displays the total progress across all files and posts (e.g., 'Overall Progress (5/10 files, 2/3 posts)').<br>"
                           "  - <b>Console</b>: Logs messages such as 'Starting download of file 1/10: [URL]' or 'Successfully downloaded: [path]'. Logs are color-coded: green for info, yellow for warnings, red for errors.<br>"
                           "- <b>Note</b>: During the download, the 'Download' button becomes disabled, the 'Cancel' button is enabled, and the 'Post Downloader' tab is temporarily disabled to prevent conflicts.<br><br>"
                           "<b>3.6 Managing Downloads</b><br>"
                           "- <b>Canceling Downloads</b>: Click the 'Cancel' button (marked with an 'X' icon) to stop all active downloads. The progress bars will turn yellow, and the labels will update to 'Downloads Terminated'. The 'Post Downloader' tab will be re-enabled.<br>"
                           "- <b>Removing Creators from Queue</b>: Click the 'X' button next to a creator URL in the 'Creator Queue' list to remove it. You'll be prompted to confirm the removal. If removed during an active download, the download for that creator's posts will be canceled.<br>"
                           "- <b>Previewing Images</b>: Select a post in the 'Posts to Download' list, then click the eye icon button below the list to preview its thumbnail (if available). Only JPG, JPEG, PNG, and GIF files are supported for preview. A modal window will open showing the image, with a progress bar while it loads.<br>"
                           "- <b>Note</b>: If no posts are selected when you click 'Download', a warning will appear in the console: '[WARNING] No posts selected for download.'<br><br>"
                           "<b>3.7 Where Files Are Saved</b><br>"
                           "- Files are saved in the directory specified in the Settings tab (default is your user directory under 'Kemono Downloader/Downloads').<br>"
                           "- The folder structure is organized as follows:<br>"
                           "  - <b>Creator Folder</b>: Named after the creator's ID (e.g., '12345678').<br>"
                           "  - <b>Post Folder</b>: Named 'post_[post_id]' within the creator folder (e.g., 'post_12345678').<br>"
                           "  - Example: If downloading from creator https://kemono.cr/patreon/user/12345678, files from post 12345678 will be saved in '[Save Directory]/12345678/post_12345678/'.<br>"
                           "- Files are named based on their original URLs, with any special characters (e.g., '/') replaced with underscores to ensure compatibility with your filesystem.<br>"
                           "- <b>File Deduplication</b>: The application uses URL hashes to detect and skip previously downloaded files, storing hash data in 'file_hashes.json' in the 'Other Files' directory.<br><br>"
                           "<b>3.8 Additional Features</b><br>"
                           "- <b>Concurrent Downloads</b>: The application supports downloading multiple files simultaneously, with the number of concurrent downloads set in the Settings tab (default is 10, adjustable between 1-10).<br>"
                           "- <b>Image Caching</b>: Thumbnails and preview images are cached in the 'Cache' directory to speed up future previews of the same image.<br>"
                           "- <b>Logging</b>: The console provides detailed logs of all operations, including post detection, file preparation, download progress, and errors. This is useful for debugging issues.<br>"
                           "- <b>Batch Processing</b>: When 'Download All Links' is enabled, the application processes creators sequentially, preparing and downloading files for each creator one at a time to manage resources efficiently.",
                "japanese": "クリエイターダウンローダータブは、Kemono.su上のクリエイターの全プロフィールからコンテンツを一括ダウンロードするために設計されています。複数のクリエイターをキューに追加し、投稿を取得し、特定のコンテンツを選択してダウンロードし、進捗を監視できます。このタブは、クリエイターの作品をアーカイブしたり、複数のクリエイターから一度にコンテンツをダウンロードするのに最適です。以下に、このタブを効果的に使用するための詳細な手順を示します：<br><br>"
                            "<b>3.1 クリエイターをキューに追加する</b><br>"
                            "- <b>ステップ1</b>：インターフェース上部の「クリエイターダウンローダー」タブをクリックして移動します。このタブはユーザー編集アイコンでマークされています。<br>"
                            "- <b>ステップ2</b>：タブの左上にある「クリエイターURLを入力」フィールドを見つけます。これは「クリエイターURLを入力（例: https://kemono.cr/patreon/user/12345678）」というプレースホルダーテキストが表示されたテキスト入力フィールドです。<br>"
                            "- <b>ステップ3</b>：Kemono.suのクリエイタープロフィールのURLを入力します。URLは次の形式である必要があります：https://kemono.cr/[service]/user/[user_id]。例: https://kemono.cr/patreon/user/12345678。<br>"
                            "- <b>ステップ4</b>：入力フィールドの横にある「キューに追加」ボタンをクリックします。このボタンはプラスアイコンと青い背景でスタイルされています。<br>"
                            "- <b>ステップ5</b>：クリエイターURLが入力フィールド下の「クリエイターキュー」リストに表示されます。リストの各エントリには以下が含まれます：<br>"
                            "  - クリエイターの投稿を取得して表示するための目アイコン。<br>"
                            "  - クリック可能なラベルとしてのクリエイターURL。<br>"
                            "  - キューからクリエイターを削除するための「X」ボタン。<br>"
                            "- <b>注意</b>：重複するURLは自動的に防止されます。すでにキューにあるURLを追加しようとすると、コンソールに警告メッセージが表示されます：「[警告] URLはすでにキューにあります。」<br><br>"
                            "<b>3.2 クリエイターの投稿を表示する</b><br>"
                            "- <b>ステップ1</b>：「クリエイターキュー」リストで、投稿を表示したいクリエイターを見つけます。<br>"
                            "- <b>ステップ2</b>：クリエイターURLの横にある目アイコンをクリックします。これにより、Kemono.suからクリエイターに関連するすべての投稿を取得するバックグラウンドタスクが開始されます。<br>"
                            "- <b>ステップ3</b>：投稿がタブの右側にある「ダウンロードする投稿」リストに表示されます。各投稿エントリには以下が含まれます：<br>"
                            "  - ダウンロード用に投稿を選択するためのチェックボックス。<br>"
                            "  - 投稿タイトル（タイトルがない場合は「投稿 [post_id]」）。<br>"
                            "  - プレビュー用にユーザーデータとして保存されたサムネイルURL（利用可能な場合）。<br>"
                            "- <b>ステップ4</b>：「ダウンロードする投稿」リスト上部の検索バーを使用して、タイトルで投稿をフィルタリングします。たとえば、「artwork」と入力すると、タイトルに「artwork」を含む投稿のみが表示されます。<br>"
                            "- <b>注意</b>：投稿が取得されている間、右下の「バックグラウンドタスク進捗」バーがループアニメーションを表示し、ラベルには「リンクから投稿を検出中...」と表示されます。完了すると、ラベルは「アイドル」に変わります。<br><br>"
                            "<b>3.3 ダウンロードオプションの設定</b><br>"
                            "- <b>ステップ1</b>：「ダウンロードオプション」グループボックス内で、ダウンロードに含めるコンテンツタイプを設定します：<br>"
                            "  - <b>メインファイル</b>：各投稿に添付された主要ファイル（例: 注目画像や動画）を含みます。デフォルトで有効。<br>"
                            "  - <b>添付ファイル</b>：投稿に添付された追加ファイル（例: ZIPファイル、追加画像）を含みます。デフォルトで有効。<br>"
                            "  - <b>コンテンツ画像</b>：投稿のコンテンツに埋め込まれた画像（例: 投稿説明内の画像）を含みます。デフォルトで有効。<br>"
                            "- <b>ステップ2</b>：「ファイル拡張子」グループボックスで、ダウンロードするファイルタイプを選択します：<br>"
                            "  - オプションにはJPG/JPEG、PNG、ZIP、MP4、GIF、PDF、7Zが含まれます。<br>"
                            "  - すべてのファイルタイプがデフォルトで有効です。ダウンロードしたくないファイルタイプのチェックを外します。<br>"
                            "  - 例: 画像のみが必要な場合、ZIP、MP4、PDF、7Zのチェックを外し、JPG/JPEG、PNG、GIFをチェックしたままにします。<br>"
                            "- <b>注意</b>：これらのオプションを変更すると、ダウンロードプロセスを開始したときにダウンロードするファイルのリストが自動的に更新されます。<br><br>"
                            "<b>3.4 ダウンロードする投稿の選択</b><br>"
                            "- <b>ステップ1</b>：「ダウンロードする投稿」リストで、ダウンロードしたい投稿の横にあるチェックボックスをオンにします。デフォルトでは投稿は選択されていません。<br>"
                            "- <b>ステップ2</b>：リスト上部の「すべてチェック」チェックボックスを使用して、表示されているすべての投稿を選択または選択解除します。検索フィルターが適用されている場合、これはフィルターされた投稿にのみ影響します。<br>"
                            "- <b>ステップ3</b>：または、「すべてのリンクをダウンロード」オプションを有効にして、手動選択せずにキュー内のすべてのクリエイターからすべてのファイルをダウンロードします：<br>"
                            "  - 有効にすると、このオプションは個別の投稿チェックボックスを無効にし、キュー内のすべてのクリエイターからすべての投稿を取得します。<br>"
                            "  - アプリケーションは手動選択を無視してすべての投稿を自動的にダウンロード用に選択します。<br>"
                            "- <b>注意</b>：リスト下の「投稿: [数]」ラベルは選択された投稿の数を反映して更新されます。「すべてのリンクをダウンロード」が有効な場合、これはキュー内のすべてのクリエイターにわたる投稿の総数を表示します。<br><br>"
                            "<b>3.5 ダウンロードの開始</b><br>"
                            "- <b>ステップ1</b>：希望する投稿を選択したか、「すべてのリンクをダウンロード」を有効にしたことを確認します。<br>"
                            "- <b>ステップ2</b>：タブの左下にある「ダウンロード」ボタンをクリックします。このボタンはダウンロードアイコンでマークされ、青い背景でスタイルされています。<br>"
                            "- <b>ステップ3</b>：アプリケーションは最初にダウンロード用のファイルを準備し、バックグラウンドタスクラベルに「ダウンロードするファイルを準備中...」と表示され、進捗バーが表示されます。<br>"
                            "- <b>ステップ4</b>：準備が完了すると、ダウンロードプロセスが開始され、以下の要素が更新されます：<br>"
                            "  - <b>ファイル進捗バー</b>：現在ダウンロード中のファイルの進捗（0%から100%）を表示します。その上のラベル（例: 「ファイル進捗 50%」）がそれに応じて更新されます。<br>"
                            "  - <b>全体進捗バー</b>：すべてのファイルと投稿にわたる全体の進捗を表示します（例: 「全体進捗 (5/10 ファイル, 2/3 投稿)」）。<br>"
                            "  - <b>コンソール</b>：ダウンロードプロセスに関するメッセージを記録します。たとえば、「ファイル 1/10 のダウンロード開始: [URL]」や「ダウンロード成功: [path]」など。ログは色分けされています：情報は緑、警告は黄、エラーは赤。<br>"
                            "- <b>注意</b>：ダウンロード中は「ダウンロード」ボタンが無効になり、「キャンセル」ボタンが有効になり、「投稿ダウンローダー」タブは競合を防ぐために一時的に無効になります。<br><br>"
                            "<b>3.6 ダウンロードの管理</b><br>"
                            "- <b>ダウンロードのキャンセル</b>：「キャンセル」ボタン（「X」アイコンでマーク）をクリックしてすべてのアクティブなダウンロードを停止します。進捗バーが黄色に変わり、ラベルが「ダウンロード中断」に更新されます。「投稿ダウンローダー」タブが再び有効になります。<br>"
                            "- <b>キューからのクリエイターの削除</b>：「クリエイターキュー」リストのクリエイターURL横の「X」ボタンをクリックして削除します。削除の確認が求められます。アクティブなダウンロード中に削除された場合、そのクリエイターの投稿のダウンロードがキャンセルされます。<br>"
                            "- <b>画像のプレビュー</b>：「ダウンロードする投稿」リストで投稿を選択し、リスト下の目アイコンボタンをクリックしてサムネイル（利用可能な場合）をプレビューします。JPG、JPEG、PNG、GIFファイルのみがプレビューに対応しています。画像を表示するモーダルウィンドウが開き、読み込み中に進捗バーが表示されます。<br>"
                            "- <b>注意</b>：「ダウンロード」をクリックしたときに投稿が選択されていない場合、コンソールに警告が表示されます：「[警告] ダウンロードする投稿が選択されていません。」<br><br>"
                            "<b>3.7 ファイルの保存場所</b><br>"
                            "- ファイルは設定タブで指定されたディレクトリに保存されます（デフォルトはユーザーディレクトリ内の「Kemono Downloader/Downloads」）。<br>"
                            "- フォルダ構造は次のように整理されています：<br>"
                            "  - <b>クリエイターフォルダ</b>：クリエイターのIDに基づいて命名されます（例: 「12345678」）。<br>"
                            "  - <b>投稿フォルダ</b>：クリエイターフォルダ内で「post_[post_id]」と命名されます（例: 「post_12345678」）。<br>"
                            "  - 例: クリエイター https://kemono.cr/patreon/user/12345678 からダウンロードする場合、投稿12345678のファイルは「[保存ディレクトリ]/12345678/post_12345678/」に保存されます。<br>"
                            "- ファイル名は元のURLに基づいて命名され、ファイルシステムとの互換性を確保するために特殊文字（例: 「/」）はアンダースコアに置き換えられます。<br>"
                            "- <b>ファイルの重複排除</b>：アプリケーションはURLハッシュを使用して以前にダウンロードされたファイルを検出しスキップし、ハッシュデータは「その他のファイル」ディレクトリの「file_hashes.json」に保存されます。<br><br>"
                            "<b>3.8 追加機能</b><br>"
                            "- <b>同時ダウンロード</b>：アプリケーションは複数のファイルを同時にダウンロードでき、同時ダウンロードの数は設定タブで設定されます（デフォルトは10、1-10の間で調整可能）。<br>"
                            "- <b>画像キャッシュ</b>：サムネイルやプレビュー画像は「キャッシュ」ディレクトリにキャッシュされ、同じ画像の将来のプレビューを高速化します。<br>",
                "korean": "크리에이터 다운로더 탭은 Kemono.su에서 크리에이터의 전체 프로필에서 콘텐츠를 대량으로 다운로드하도록 설계되었습니다. 여러 크리에이터를 대기열에 추가하고, 그들의 게시물을 가져오며, 다운로드할 특정 콘텐츠를 선택하고 진행 상황을 모니터링할 수 있습니다. 이 탭은 크리에이터의 작업을 아카이빙하거나 여러 크리에이터의 콘텐츠를 한 번에 다운로드하는 데 이상적입니다. 아래는 이 탭을 효과적으로 사용하는 자세한 단계입니다:<br><br>"
                          "<b>3.1 크리에이터를 대기열에 추가하기</b><br>"
                          "- <b>단계 1</b>: 인터페이스 상단의 '크리에이터 다운로더' 탭을 클릭하여 이동합니다. 이 탭은 사용자 편집 아이콘으로 표시됩니다.<br>"
                          "- <b>단계 2</b>: 탭의 좌측 상단에 있는 '크리에이터 URL 입력' 필드를 찾습니다. 이 필드는 '크리에이터 URL 입력(예: https://kemono.cr/patreon/user/12345678)'라는 플레이스홀더 텍스트가 있는 텍스트 입력 필드입니다.<br>"
                          "- <b>단계 3</b>: Kemono.su의 크리에이터 프로필 URL을 입력합니다. URL은 다음 형식을 따라야 합니다: https://kemono.cr/[service]/user/[user_id]. 예: https://kemono.cr/patreon/user/12345678.<br>"
                          "- <b>단계 4</b>: 입력 필드 옆의 '대기열에 추가' 버튼을 클릭합니다. 이 버튼은 플러스 아이콘과 파란색 배경으로 스타일링되어 있습니다.<br>"
                          "- <b>단계 5</b>: 크리에이터 URL이 입력 필드 아래의 '크리에이터 대기열' 목록에 나타납니다. 목록의 각 항목에는 다음이 포함됩니다:<br>"
                          "  - 크리에이터의 게시물을 가져오고 보기 위한 눈 아이콘.<br>"
                          "  - 클릭 가능한 레이블로 표시된 크리에이터 URL.<br>"
                          "  - 대기열에서 크리에이터를 제거하기 위한 'X' 버튼.<br>"
                          "- <b>참고</b>: 중복 URL은 자동으로 방지됩니다. 이미 대기열에 있는 URL을 추가하려고 하면 콘솔에 경고 메시지가 표시됩니다: '[경고] URL이 이미 대기열에 있습니다.'<br><br>"
                          "<b>3.2 크리에이터 게시물 보기</b><br>"
                          "- <b>단계 1</b>: '크리에이터 대기열' 목록에서 게시물을 보고 싶은 크리에이터를 찾습니다.<br>"
                          "- <b>단계 2</b>: 크리에이터 URL 옆의 눈 아이콘을 클릭합니다. 그러면 Kemono.su에서 크리에이터와 관련된 모든 게시물을 가져오는 백그라운드 작업이 시작됩니다.<br>"
                          "- <b>단계 3</b>: 게시물이 탭의 오른쪽에 있는 '다운로드할 게시물' 목록에 표시됩니다. 각 게시물 항목에는 다음이 포함됩니다:<br>"
                          "  - 다운로드를 위해 게시물을 선택하는 체크박스.<br>"
                          "  - 게시물 제목(제목이 없는 경우 '게시물 [post_id]')<br>"
                          "  - 미리보기를 위해 사용자 데이터로 저장된 썸네일 URL(사용 가능한 경우).<br>"
                          "- <b>단계 4</b>: '다운로드할 게시물' 목록 위의 검색창을 사용하여 제목으로 게시물을 필터링합니다. 예를 들어, 'artwork'를 입력하면 제목에 'artwork'가 포함된 게시물만 표시됩니다.<br>"
                          "- <b>참고</b>: 게시물이 가져와지는 동안 오른쪽 하단의 '백그라운드 작업 진행률' 바가 루프 애니메이션을 표시하며, 레이블은 '링크에서 게시물 감지 중...'이라고 표시됩니다. 완료되면 레이블이 '대기 중'으로 변경됩니다.<br><br>"
                          "<b>3.3 다운로드 옵션 설정</b><br>"
                          "- <b>단계 1</b>: '다운로드 옵션' 그룹 박스에서 다운로드에 포함할 콘텐츠 유형을 설정합니다:<br>"
                          "  - <b>주요 파일</b>: 각 게시물에 첨부된 주요 파일(예: 주요 이미지 또는 비디오)을 포함합니다. 기본적으로 활성화됨.<br>"
                          "  - <b>첨부 파일</b>: 게시물에 첨부된 추가 파일(예: ZIP 파일, 추가 이미지)을 포함합니다. 기본적으로 활성화됨.<br>"
                          "  - <b>콘텐츠 이미지</b>: 게시물 콘텐츠에 포함된 이미지(예: 게시물 설명의 이미지)를 포함합니다. 기본적으로 활성화됨.<br>"
                          "- <b>단계 2</b>: '파일 확장자' 그룹 박스에서 다운로드할 파일 유형을 선택합니다:<br>"
                          "  - 옵션에는 JPG/JPEG, PNG, ZIP, MP4, GIF, PDF, 7Z가 포함됩니다.<br>"
                          "  - 모든 파일 유형이 기본적으로 활성화되어 있습니다. 다운로드하고 싶지 않은 파일 유형의 체크를 해제합니다.<br>"
                          "  - 예: 이미지 파일만 원한다면 ZIP, MP4, PDF, 7Z의 체크를 해제하고 JPG/JPEG, PNG, GIF를 체크 상태로 둡니다.<br>"
                          "- <b>참고</b>: 이러한 옵션을 변경하면 다운로드 프로세스를 시작할 때 다운로드할 파일 목록이 자동으로 업데이트됩니다.<br><br>"
                          "<b>3.4 다운로드할 게시물 선택</b><br>"
                          "- <b>단계 1</b>: '다운로드할 게시물' 목록에서 다운로드하고 싶은 게시물 옆의 체크박스를 선택합니다. 기본적으로 게시물이 선택되어 있지 않습니다.<br>"
                          "- <b>단계 2</b>: 목록 위의 '모두 선택' 체크박스를 사용하여 표시된 모든 게시물을 선택하거나 선택 해제합니다. 검색 필터가 적용된 경우, 이는 필터링된 게시물에만 영향을 미칩니다.<br>"
                          "- <b>단계 3</b>: 또는 '모든 링크 다운로드' 옵션을 활성화하여 수동 선택 없이 대기열에 있는 모든 크리에이터의 모든 파일을 다운로드합니다:<br>"
                          "  - 활성화되면 이 옵션은 개별 게시물 체크박스를 비활성화하고 대기열에 있는 모든 크리에이터의 모든 게시물을 가져옵니다.<br>"
                          "  - 애플리케이션은 수동 선택을 무시하고 모든 게시물을 자동으로 다운로드 대상으로 선택합니다.<br>"
                          "- <b>참고</b>: 목록 아래의 '게시물: [숫자]' 레이블은 선택된 게시물 수를 반영하여 업데이트됩니다. '모든 링크 다운로드'가 활성화되면 대기열에 있는 모든 크리에이터의 총 게시물 수를 표시합니다.<br><br>"
                          "<b>3.5 다운로드 시작</b><br>"
                          "- <b>단계 1</b>: 원하는 게시물을 선택했거나 '모든 링크 다운로드'를 활성화했는지 확인합니다.<br>"
                          "- <b>단계 2</b>: 탭의 좌측 하단에 있는 '다운로드' 버튼을 클릭합니다. 이 버튼은 다운로드 아이콘으로 표시되며 파란색 배경으로 스타일링되어 있습니다.<br>"
                          "- <b>단계 3</b>: 애플리케이션이 먼저 다운로드할 파일을 준비하며, 백그라운드 작업 레이블에 '다운로드할 파일 준비 중...'이 표시되고 진행률 바가 나타납니다.<br>"
                          "- <b>단계 4</b>: 준비가 완료되면 다운로드 프로세스가 시작되고 다음 요소들이 업데이트됩니다:<br>"
                          "  - <b>파일 진행률 바</b>: 현재 다운로드 중인 파일의 진행률(0%에서 100%)을 표시합니다. 위의 레이블(예: '파일 진행률 50%')이 그에 따라 업데이트됩니다.<br>"
                          "  - <b>전체 진행률 바</b>: 모든 파일과 게시물에 걸친 총 진행률을 표시합니다(예: '전체 진행률 (5/10 파일, 2/3 게시물)').<br>"
                          "  - <b>콘솔</b>: '파일 1/10 다운로드 시작: [URL]' 또는 '다운로드 성공: [경로]'와 같은 메시지를 기록합니다. 로그는 색상으로 구분됩니다: 정보는 녹색, 경고는 노란색, 오류는 빨간색.<br>"
                          "- <b>참고</b>: 다운로드 중에는 '다운로드' 버튼이 비활성화되고, '취소' 버튼이 활성화되며, '게시물 다운로더' 탭은 충돌을 방지하기 위해 일시적으로 비활성화됩니다.<br><br>"
                          "<b>3.6 다운로드 관리</b><br>"
                          "- <b>다운로드 취소</b>: '취소' 버튼('X' 아이콘으로 표시)을 클릭하여 모든 활성 다운로드를 중지합니다. 진행률 바가 노란색으로 변하고 레이블이 '다운로드 중단됨'으로 업데이트됩니다. '게시물 다운로더' 탭이 다시 활성화됩니다.<br>"
                          "- <b>대기열에서 크리에이터 제거</b>: '크리에이터 대기열' 목록에서 크리에이터 URL 옆의 'X' 버튼을 클릭하여 제거합니다. 제거 확인 메시지가 표시됩니다. 활성 다운로드 중에 제거되면 해당 크리에이터의 게시물 다운로드가 취소됩니다.<br>"
                          "- <b>이미지 미리보기</b>: '다운로드할 게시물' 목록에서 게시물을 선택한 후 목록 아래의 눈 아이콘 버튼을 클릭하여 썸네일(사용 가능한 경우)을 미리 봅니다. JPG, JPEG, PNG, GIF 파일만 미리보기가 지원됩니다. 이미지를 표시하는 모달 창이 열리며 로드 중에는 진행률 바가 표시됩니다.<br>"
                          "- <b>참고</b>: '다운로드'를 클릭했을 때 선택된 게시물이 없으면 콘솔에 경고가 표시됩니다: '[경고] 다운로드할 게시물이 선택되지 않았습니다.'<br><br>"
                          "<b>3.7 파일 저장 위치</b><br>"
                          "- 파일은 설정 탭에서 지정된 디렉토리에 저장됩니다(기본값은 사용자 디렉토리 내 'Kemono Downloader/Downloads').<br>"
                          "- 폴더 구조는 다음과 같이 구성됩니다:<br>"
                          "  - <b>크리에이터 폴더</b>: 크리에이터의 ID로 명명됩니다(예: '12345678').<br>"
                          "  - <b>게시물 폴더</b>: 크리에이터 폴더 내에서 'post_[post_id]'로 명명됩니다(예: 'post_12345678').<br>"
                          "  - 예: 크리에이터 https://kemono.cr/patreon/user/12345678에서 다운로드하면 게시물 12345678의 파일은 '[저장 디렉토리]/12345678/post_12345678/'에 저장됩니다.<br>"
                          "- 파일 이름은 원래 URL을 기반으로 하며, 파일 시스템 호환성을 보장하기 위해 특수 문자(예: '/')는 밑줄로 대체됩니다.<br>"
                          "- <b>파일 중복 제거</b>: 애플리케이션은 URL 해시를 사용하여 이전에 다운로드된 파일을 감지하고 건너뛰며, 해시 데이터는 '기타 파일' 디렉토리의 'file_hashes.json'에 저장됩니다.<br><br>"
                          "<b>3.8 추가 기능</b><br>"
                          "- <b>동시 다운로드</b>: 애플리케이션은 여러 파일을 동시에 다운로드할 수 있으며, 동시 다운로드 수는 설정 탭에서 설정됩니다(기본값은 10, 1-10 사이에서 조정 가능).<br>"
                          "- <b>이미지 캐싱</b>: 썸네일 및 미리보기 이미지는 '캐시' 디렉토리에 캐시되어 동일한 이미지의 향후 미리보기를 빠르게 합니다.<br>"
                          "- <b>로깅</b>: 콘솔은 게시물 감지, 파일 준비, 다운로드 진행 상황, 오류를 포함한 모든 작업에 대한 자세한 로그를 제공하여 문제 디버깅에 유용합니다.<br>"
                          "- <b>배치 처리</b>: '모든 링크 다운로드'가 활성화되면 애플리케이션은 자원을 효율적으로 관리하기 위해 각 크리에이터를 순차적으로 처리하며, 한 번에 한 크리에이터의 파일을 준비하고 다운로드합니다."
            },
            "help_settings_title": {
                "english": "4. Using the Settings Tab",
                "japanese": "4. 設定タブの使用",
                "korean": "4. 설정 탭 사용",
                "chinese-simplified": "4. 使用设置选项卡"
            },
            "help_settings_text": {
                "english": "The Settings tab allows you to customize the behavior and appearance of the Kemono Downloader to suit your preferences. From changing the save directory to adjusting the number of simultaneous downloads, this tab provides all the tools you need to optimize your experience. Below are the detailed options available in this tab:<br><br>"
                           "<b>4.1 General Settings</b><br>"
                           "- <b>Save Directory</b>: Specify where downloaded files are saved.<br>"
                           "  - Default: Your user directory under 'Kemono Downloader/Downloads'.<br>"
                           "  - Click the 'Browse' button next to the text field to open a file dialog and select a new directory.<br>"
                           "  - Example: Change it to 'D:/Kemono Downloads' to save files there instead.<br>"
                           "- <b>Max Simultaneous Downloads</b>: Control how many files are downloaded at once.<br>"
                           "  - Default: 10.<br>"
                           "  - Use the spin box to adjust between 1 and 10. Lower values reduce bandwidth usage but slow down the process; higher values speed it up but may strain your connection.<br><br>"
                           "<b>4.2 Saving Changes</b><br>"
                           "- Changes to settings like 'Save Directory', 'Max Simultaneous Downloads', and 'Language' are saved automatically when adjusted.<br>"
                           "- Actions like 'Clear Cache' and 'Reset File Hashes' require manual confirmation via their respective buttons.<br>"
                           "- There’s no 'Save' button; all settings persist across sessions unless manually reset (e.g., via 'Reset Hashes').<br><br>"
                           "<b>4.3 Notes</b><br>"
                           "- Changing the 'Save Directory' only affects new downloads; existing files remain in their original locations.<br>"
                           "- Adjusting 'Max Simultaneous Downloads' during an active download won’t affect the current session but will apply to the next one.<br>"
                           "- If you disable 'Enable Logging', you’ll still see critical errors in the console, but routine info and warnings will be hidden.",
                "japanese": "設定タブでは、ケモノダウンローダーの動作や外観を好みに合わせてカスタマイズできます。保存ディレクトリの変更から同時ダウンロード数の調整まで、このタブには体験を最適化するために必要なすべてのツールが揃っています。以下に、このタブで利用可能な詳細なオプションを示します：<br><br>"
                            "<b>4.1 一般設定</b><br>"
                            "- <b>保存ディレクトリ</b>：ダウンロードしたファイルの保存先を指定します。<br>"
                            "  - デフォルト：ユーザーディレクトリ内の「Kemono Downloader/Downloads」。<br>"
                            "  - テキストフィールド横の「参照」ボタンをクリックしてファイルダイアログを開き、新しいディレクトリを選択します。<br>"
                            "  - 例：「D:/Kemono Downloads」に変更すると、そこにファイルが保存されます。<br>"
                            "- <b>最大同時ダウンロード数</b>：一度にダウンロードするファイル数を制御します。<br>"
                            "  - デフォルト：10。<br>"
                            "  - スピンボックスを使用して1から10の間で調整します。低い値は帯域幅使用量を減らしますが処理が遅くなり、高い値は速度を上げますが接続に負担をかける可能性があります。<br><br>"
                            "<b>4.2 変更の保存</b><br>"
                            "- 「保存ディレクトリ」、「最大同時ダウンロード数」、「言語」の設定変更は調整時に自動的に保存されます。<br>"
                            "- 「キャッシュのクリア」や「ファイルハッシュのリセット」などのアクションは、それぞれのボタンを介して手動で確認が必要です。<br>"
                            "- 「保存」ボタンはありません。すべての設定は手動でリセットされない限り（例：「ハッシュのリセット」）、セッション間で保持されます。<br><br>"
                            "<b>4.3 注意事項</b><br>"
                            "- 「保存ディレクトリ」の変更は新しいダウンロードにのみ影響し、既存のファイルは元の場所に残ります。<br>"
                            "- アクティブなダウンロード中に「最大同時ダウンロード数」を調整しても現在のセッションには影響しませんが、次のセッションに適用されます。<br>"
                            "- 「ログを有効にする」を無効にしても、コンソールには重大なエラーが表示されますが、通常の情報や警告は非表示になります。",
                "korean": "설정 탭을 사용하면 케모노 다운로더의 동작과 외관을 사용자의 선호도에 맞게 사용자 정의할 수 있습니다. 저장 디렉토리 변경부터 동시 다운로드 수 조정까지, 이 탭은 사용 경험을 최적화하는 데 필요한 모든 도구를 제공합니다. 아래는 이 탭에서 사용할 수 있는 자세한 옵션입니다:<br><br>"
                          "<b>4.1 일반 설정</b><br>"
                          "- <b>저장 디렉토리</b>: 다운로드한 파일이 저장될 위치를 지정합니다.<br>"
                          "  - 기본값: 사용자 디렉토리 내 'Kemono Downloader/Downloads'.<br>"
                          "  - 텍스트 필드 옆의 '찾아보기' 버튼을 클릭하여 파일 대화 상자를 열고 새 디렉토리를 선택합니다.<br>"
                          "  - 예: 'D:/Kemono Downloads'로 변경하면 파일이 그곳에 저장됩니다.<br>"
                          "- <b>최대 동시 다운로드 수</b>: 한 번에 다운로드되는 파일 수를 제어합니다.<br>"
                          "  - 기본값: 10.<br>"
                          "  - 스핀 박스를 사용하여 1에서 10 사이로 조정합니다. 낮은 값은 대역폭 사용을 줄이지만 프로세스가 느려지고, 높은 값은 속도를 높이지만 연결에 부담을 줄 수 있습니다.<br><br>"
                          "<b>4.2 변경 사항 저장</b><br>"
                          "- '저장 디렉토리', '최대 동시 다운로드 수', '언어'와 같은 설정 변경은 조정 시 자동으로 저장됩니다.<br>"
                          "- '캐시 지우기'와 '파일 해시 초기화'와 같은 작업은 해당 버튼을 통해 수동으로 확인해야 합니다.<br>"
                          "- '저장' 버튼은 없습니다. 모든 설정은 수동으로 초기화되지 않는 한(예: '해시 초기화') 세션 간에 유지됩니다.<br><br>"
                          "<b>4.3 참고 사항</b><br>"
                          "- '저장 디렉토리'를 변경하면 새 다운로드에만 영향을 미치며 기존 파일은 원래 위치에 남습니다.<br>"
                          "- 활성 다운로드 중에 '최대 동시 다운로드 수'를 조정해도 현재 세션에는 영향을 주지 않지만 다음 세션에 적용됩니다.<br>"
                          "- '로깅 활성화'를 비활성화하면 콘솔에 치명적인 오류만 표시되며, 일상적인 정보와 경고는 숨겨집니다."
            },
            "help_help_tab_title": {
                "english": "5. Using the Help Tab",
                "japanese": "5. ヘルプタブの使用",
                "korean": "5. 도움말 탭 사용",
                "chinese-simplified": "5. 使用帮助选项卡"
            },
            "help_help_tab_text": {
                "english": "The Help tab provides a comprehensive user manual for the Kemono Downloader, guiding you through every aspect of the application. Whether you’re a new user or need a refresher, this tab is your go-to resource for understanding how to use the tool effectively.<br><br>"
                           "<b>5.1 Accessing the Help Tab</b><br>"
                           "- Navigate to the 'Help' tab by clicking its label at the top of the interface. The tab is marked with a question mark icon.<br>"
                           "- The content is displayed in a scrollable area with a dark blue-gray background (#2A3B5A), matching the default theme.<br><br>"
                           "<b>5.2 Content Overview</b><br>"
                           "- <b>Introduction</b>: A welcome message and overview of the application’s key features.<br>"
                           "- <b>Getting Started</b>: Instructions for launching the application and understanding the main interface.<br>"
                           "- <b>Post Downloader Tab</b>: Detailed steps for downloading content from specific posts.<br>"
                           "- <b>Creator Downloader Tab</b>: Instructions for bulk downloading from creator profiles.<br>"
                           "- <b>Settings Tab</b>: Explanation of all customizable options.<br>"
                           "- <b>Help Tab</b>: This section, describing the purpose and structure of the Help tab.<br>"
                           "- <b>Troubleshooting</b>: Common issues and their solutions.<br>"
                           "- <b>Contact and Support</b>: Information on how to get help or report issues.<br><br>"
                           "<b>5.3 Using the Help Tab</b><br>"
                           "- Scroll through the sections using the vertical scrollbar on the right side of the tab.<br>"
                           "- Each section is clearly labeled with a bold heading (e.g., '1. Getting Started') in white text, followed by detailed explanations in light gray (#D0D0D0).<br>"
                           "- The text is formatted with HTML tags (e.g., <b> for bold) to highlight important points.<br>"
                           "- The content dynamically updates to reflect the language selected in the Settings tab (English, Japanese, or Korean).<br><br>"
                           "<b>5.4 Notes</b><br>"
                           "- The Help tab is static and does not require an internet connection to view, as all content is embedded in the application.<br>"
                           "- If you encounter an issue not covered here, refer to the 'Troubleshooting' or 'Contact and Support' sections for further assistance.",
                "japanese": "ヘルプタブは、ケモノダウンローダーの包括的なユーザーマニュアルを提供し、アプリケーションのあらゆる側面をガイドします。初めてのユーザーでも、リフレッシュが必要な場合でも、このタブはツールを効果的に使用する方法を理解するための主要なリソースです。<br><br>"
                            "<b>5.1 ヘルプタブへのアクセス</b><br>"
                            "- インターフェース上部の「ヘルプ」タブをクリックして移動します。このタブは疑問符アイコンでマークされています。<br>"
                            "- コンテンツは、デフォルトテーマに合わせた暗い青灰色の背景（#2A3B5A）を持つスクロール可能なエリアに表示されます。<br><br>"
                            "<b>5.2 コンテンツの概要</b><br>"
                            "- <b>イントロダクション</b>：ウェルカムメッセージとアプリケーションの主要機能の概要。<br>"
                            "- <b>はじめに</b>：アプリケーションの起動とメインインターフェースの理解に関する指示。<br>"
                            "- <b>投稿ダウンローダータブ</b>：特定の投稿からコンテンツをダウンロードする詳細な手順。<br>"
                            "- <b>クリエイターダウンローダータブ</b>：クリエイタープロフィールからの一括ダウンロードに関する指示。<br>"
                            "- <b>設定タブ</b>：すべてのカスタマイズ可能なオプションの説明。<br>"
                            "- <b>ヘルプタブ</b>：このセクションで、ヘルプタブの目的と構造を説明します。<br>"
                            "- <b>トラブルシューティング</b>：一般的な問題とその解決策。<br>"
                            "- <b>連絡とサポート</b>：ヘルプの取得方法や問題の報告方法に関する情報。<br><br>"
                            "<b>5.3 ヘルプタブの使用</b><br>"
                            "- タブの右側にある垂直スクロールバーを使用してセクションをスクロールします。<br>"
                            "- 各セクションは、白いテキストで太字の見出し（例：「1. はじめに」）で明確にラベル付けされ、その後に薄い灰色（#D0D0D0）で詳細な説明が続きます。<br>"
                            "- テキストは重要なポイントを強調するためにHTMLタグ（例：<b>で太字）でフォーマットされています。<br>"
                            "- コンテンツは、設定タブで選択した言語（英語、日本語、韓国語）を反映して動的に更新されます。<br><br>"
                            "<b>5.4 注意事項</b><br>"
                            "- ヘルプタブは静的であり、すべてのコンテンツがアプリケーションに埋め込まれているため、表示にインターネット接続は必要ありません。<br>"
                            "- ここでカバーされていない問題に遭遇した場合は、「トラブルシューティング」または「連絡とサポート」セクションを参照してさらなる支援を受けてください。",
                "korean": "도움말 탭은 케모노 다운로더에 대한 포괄적인 사용자 매뉴얼을 제공하여 애플리케이션의 모든 측면을 안내합니다. 신규 사용자가 되든, 복습이 필요하든, 이 탭은 도구를 효과적으로 사용하는 방법을 이해하기 위한 주요 자료입니다.<br><br>"
                          "<b>5.1 도움말 탭 접근</b><br>"
                          "- 인터페이스 상단의 '도움말' 탭을 클릭하여 이동합니다. 이 탭은 물음표 아이콘으로 표시됩니다.<br>"
                          "- 콘텐츠는 기본 테마와 일치하는 어두운 청회색 배경(#2A3B5A)을 가진 스크롤 가능한 영역에 표시됩니다.<br><br>"
                          "<b>5.2 콘텐츠 개요</b><br>"
                          "- <b>소개</b>: 환영 메시지와 애플리케이션의 주요 기능 개요.<br>"
                          "- <b>시작하기</b>: 애플리케이션 실행 및 메인 인터페이스 이해에 대한 지침.<br>"
                          "- <b>게시물 다운로더 탭</b>: 특정 게시물에서 콘텐츠를 다운로드하는 자세한 단계.<br>"
                          "- <b>크리에이터 다운로더 탭</b>: 크리에이터 프로필에서 대량 다운로드에 대한 지침.<br>"
                          "- <b>설정 탭</b>: 모든 사용자 정의 옵션 설명.<br>"
                          "- <b>도움말 탭</b>: 이 섹션으로, 도움말 탭의 목적과 구조를 설명합니다.<br>"
                          "- <b>문제 해결</b>: 일반적인 문제와 해결 방법.<br>"
                          "- <b>연락 및 지원</b>: 도움을 받거나 문제를 보고하는 방법에 대한 정보.<br><br>"
                          "<b>5.3 도움말 탭 사용</b><br>"
                          "- 탭 오른쪽의 수직 스크롤바를 사용하여 섹션을 스크롤합니다.<br>"
                          "- 각 섹션은 흰색 텍스트로 굵은 제목(예: '1. 시작하기')으로 명확히 표시되며, 그 뒤에 연한 회색(#D0D0D0)으로 자세한 설명이 이어집니다.<br>"
                          "- 텍스트는 중요한 포인트를 강조하기 위해 HTML 태그(예: <b>로 굵게)를 사용하여 포맷팅됩니다.<br>"
                          "- 콘텐츠는 설정 탭에서 선택한 언어(영어, 일본어, 한국어)를 반영하여 동적으로 업데이트됩니다.<br><br>"
                          "<b>5.4 참고 사항</b><br>"
                          "- 도움말 탭은 정적이며 모든 콘텐츠가 애플리케이션에 내장되어 있어 보기에 인터넷 연결이 필요하지 않습니다.<br>"
                          "- 여기서 다루지 않은 문제에 직면하면 '문제 해결' 또는 '연락 및 지원' 섹션을 참조하여 추가 도움을 받으세요."
            },
            "help_troubleshooting_title": {
                "english": "6. Troubleshooting",
                "japanese": "6. トラブルシューティング",
                "korean": "6. 문제 해결",
                "chinese-simplified": "6. 故障排除"
            },
            "help_troubleshooting_text": {
                "english": "This section addresses common issues you might encounter while using the Kemono Downloader and provides solutions to resolve them. If your problem isn’t listed here, refer to the 'Contact and Support' section for further assistance.<br><br>"
                           "<b>6.1 Download Fails with 'Connection Error'</b><br>"
                           "- <b>Cause</b>: No internet connection or Kemono.cr is temporarily unavailable.<br>"
                           "- <b>Solution</b>: Check your internet connection. Wait a few minutes and try again, as the site may be down for maintenance. Check the console for specific error messages (e.g., '[ERROR] Failed to connect to URL').<br><br>"
                           "<b>6.2 Files Are Not Downloading</b><br>"
                           "- <b>Cause</b>: No files selected, or the post/creator URL is invalid.<br>"
                           "- <b>Solution</b>: Ensure you’ve selected files or posts in the 'Files to Download' or 'Posts to Download' lists. Verify the URL format (e.g., https://kemono.cr/patreon/user/12345678/post/12345678). Check the console for warnings like '[WARNING] No files found for URL'.<br><br>"
                           "<b>6.3 Downloads Are Slow</b><br>"
                           "- <b>Cause</b>: Too many simultaneous downloads or a slow internet connection.<br>"
                           "- <b>Solution</b>: Reduce the 'Max Simultaneous Downloads' value in the Settings tab (e.g., from 10 to 5). Test your internet speed to ensure it’s not the bottleneck.<br><br>"
                           "<b>6.4 Image Previews Don’t Load</b><br>"
                           "- <b>Cause</b>: Corrupted cache or network issues.<br>"
                           "- <b>Solution</b>: Go to the Settings tab and click 'Clear Cache' to remove temporary files. Try previewing again. If the issue persists, check your internet connection or the file’s availability on Kemono.cr.<br><br>"
                           "<b>6.5 Duplicate Files Are Downloaded</b><br>"
                           "- <b>Cause</b>: The 'file_hashes.json' file is missing or corrupted.<br>"
                           "- <b>Solution</b>: In the Settings tab, click 'Reset File Hashes' to clear the deduplication data, then re-download. The application will rebuild the hash file to prevent future duplicates.<br><br>"
                           "<b>6.6 Application Crashes or Freezes</b><br>"
                           "- <b>Cause</b>: Resource overload or a bug.<br>"
                           "- <b>Solution</b>: Restart the application. Reduce 'Max Simultaneous Downloads' to lessen the load. Check the console logs for error messages and report them via the GitHub link in the 'Contact and Support' section.<br><br>"
                           "<b>6.7 Language Doesn’t Change</b><br>"
                           "- <b>Cause</b>: UI refresh issue.<br>"
                           "- <b>Solution</b>: After selecting a new language in the Settings tab, restart the application if the change doesn’t take effect immediately.",
                "japanese": "このセクションでは、ケモノダウンローダーの使用中に遭遇する可能性のある一般的な問題とその解決策を扱います。ここに記載されていない問題が発生した場合は、「連絡とサポート」セクションを参照してさらなる支援を受けてください。<br><br>"
                            "<b>6.1 「接続エラー」でダウンロードが失敗する</b><br>"
                            "- <b>原因</b>：インターネット接続がないか、Kemono.suが一時的に利用できない。<br>"
                            "- <b>解決策</b>：インターネット接続を確認してください。サイトがメンテナンス中の可能性があるため、数分待ってから再試行してください。コンソールで具体的なエラーメッセージ（例：「[エラー] URLへの接続に失敗しました」）を確認してください。<br><br>"
                            "<b>6.2 ファイルがダウンロードされない</b><br>"
                            "- <b>原因</b>：ファイルが選択されていないか、投稿/クリエイターURLが無効。<br>"
                            "- <b>解決策</b>：「ダウンロードするファイル」または「ダウンロードする投稿」リストでファイルまたは投稿を選択していることを確認してください。URL形式（例：https://kemono.cr/patreon/user/12345678/post/12345678）が正しいか確認してください。コンソールで「[警告] URLにファイルが見つかりませんでした」などの警告を確認してください。<br><br>"
                            "<b>6.3 ダウンロードが遅い</b><br>"
                            "- <b>原因</b>：同時ダウンロード数が多すぎるか、インターネット接続が遅い。<br>"
                            "- <b>解決策</b>：設定タブで「最大同時ダウンロード数」を減らしてください（例：10から5へ）。インターネット速度をテストしてボトルネックでないことを確認してください。<br><br>"
                            "<b>6.4 画像プレビューが読み込まれない</b><br>"
                            "- <b>原因</b>：キャッシュの破損またはネットワークの問題。<br>"
                            "- <b>解決策</b>：設定タブに移動し、「キャッシュのクリア」をクリックして一時ファイルを削除してください。再度プレビューを試してください。問題が続く場合は、インターネット接続やKemono.suでのファイルの可用性を確認してください。<br><br>"
                            "<b>6.5 重複ファイルがダウンロードされる</b><br>"
                            "- <b>原因</b>：「file_hashes.json」ファイルが欠落しているか破損している。<br>"
                            "- <b>解決策</b>：設定タブで「ファイルハッシュのリセット」をクリックして重複排除データをクリアし、再ダウンロードしてください。アプリケーションは将来の重複を防ぐためにハッシュファイルを再構築します。<br><br>"
                            "<b>6.6 アプリケーションがクラッシュまたはフリーズする</b><br>"
                            "- <b>原因</b>：リソースの過負荷またはバグ。<br>"
                            "- <b>解決策</b>：アプリケーションを再起動してください。「最大同時ダウンロード数」を減らして負荷を軽減してください。コンソールログでエラーメッセージを確認し、「連絡とサポート」セクションのGitHubリンクを介して報告してください。<br><br>"
                            "<b>6.7 言語が変更されない</b><br>"
                            "- <b>原因</b>：UIのリフレッシュ問題。<br>"
                            "- <b>解決策</b>：設定タブで新しい言語を選択した後、変更が即座に反映されない場合はアプリケーションを再起動してください。",
                "korean": "이 섹션에서는 케모노 다운로더 사용 중 발생할 수 있는 일반적인 문제와 해결 방법을 다룹니다. 여기에 나열되지 않은 문제가 발생하면 '연락 및 지원' 섹션을 참조하여 추가 지원을 받으세요.<br><br>"
                          "<b>6.1 '연결 오류'로 다운로드 실패</b><br>"
                          "- <b>원인</b>: 인터넷 연결이 없거나 Kemono.su가 일시적으로 사용 불가능.<br>"
                          "- <b>해결책</b>: 인터넷 연결을 확인하세요. 사이트가 유지보수 중일 수 있으니 몇 분 기다린 후 다시 시도하세요. 콘솔에서 구체적인 오류 메시지(예: '[오류] URL 연결 실패')를 확인하세요.<br><br>"
                          "<b>6.2 파일이 다운로드되지 않음</b><br>"
                          "- <b>원인</b>: 파일이 선택되지 않았거나 게시물/크리에이터 URL이 유효하지 않음.<br>"
                          "- <b>해결책</b>: '다운로드할 파일' 또는 '다운로드할 게시물' 목록에서 파일이나 게시물을 선택했는지 확인하세요. URL 형식이 올바른지(예: https://kemono.cr/patreon/user/12345678/post/12345678) 확인하세요. 콘솔에서 '[경고] URL에서 파일을 찾을 수 없음'과 같은 경고를 확인하세요.<br><br>"
                          "<b>6.3 다운로드 속도가 느림</b><br>"
                          "- <b>원인</b>: 동시 다운로드가 너무 많거나 인터넷 연결이 느림.<br>"
                          "- <b>해결책</b>: 설정 탭에서 '최대 동시 다운로드 수'를 줄이세요(예: 10에서 5로). 인터넷 속도를 테스트하여 병목 현상이 아닌지 확인하세요.<br><br>"
                          "<b>6.4 이미지 미리보기가 로드되지 않음</b><br>"
                          "- <b>원인</b>: 캐시 손상 또는 네트워크 문제.<br>"
                          "- <b>해결책</b>: 설정 탭으로 이동하여 '캐시 지우기'를 클릭해 임시 파일을 삭제하세요. 다시 미리보기를 시도하세요. 문제가 지속되면 인터넷 연결이나 Kemono.su에서 파일의 가용성을 확인하세요.<br><br>"
                          "<b>6.5 중복 파일이 다운로드됨</b><br>"
                          "- <b>원인</b>: 'file_hashes.json' 파일이 없거나 손상됨.<br>"
                          "- <b>해결책</b>: 설정 탭에서 '파일 해시 초기화'를 클릭하여 중복 제거 데이터를 지우고 다시 다운로드하세요. 애플리케이션이 해시 파일을 재구축하여 향후 중복을 방지합니다.<br><br>"
                          "<b>6.6 애플리케이션이 충돌하거나 멈춤</b><br>"
                          "- <b>원인</b>: 자원 과부하 또는 버그.<br>"
                          "- <b>해결책</b>: 애플리케이션을 재시작하세요. '최대 동시 다운로드 수'를 줄여 부하를 줄이세요. 콘솔 로그에서 오류 메시지를 확인하고 '연락 및 지원' 섹션의 GitHub 링크를 통해 보고하세요.<br><br>"
                          "<b>6.7 언어가 변경되지 않음</b><br>"
                          "- <b>원인</b>: UI 새로고침 문제.<br>"
                          "- <b>해결책</b>: 설정 탭에서 새 언어를 선택한 후 변경이 즉시 적용되지 않으면 애플리케이션을 재시작하세요."
            },
            "help_support_title": {
                "english": "7. Contact and Support",
                "japanese": "7. 連絡とサポート",
                "korean": "7. 연락 및 지원",
                "chinese-simplified": "7. 联系和支持"
            },
            "help_support_text": {
                "english": "If you need further assistance or want to report a bug, this section provides the necessary information to get help.<br><br>"
                           "<b>7.1 GitHub Repository</b><br>"
                           "- The Kemono Downloader is an open-source project hosted on GitHub.<br>"
                           "- Visit the project page at: <a href='https://github.com/VoxDroid'>github.com/VoxDroid</a>.<br>"
                           "- Check the 'Issues' tab for existing bug reports or feature requests. If your issue isn’t listed, create a new issue with the following details:<br>"
                           "  - A clear description of the problem or request.<br>"
                           "  - Steps to reproduce the issue (if applicable).<br>"
                           "  - Any relevant console logs or screenshots.<br>"
                           "- The developer, VoxDroid, monitors the repository and will respond to issues as time permits.<br><br>"
                           "<b>7.2 Updates</b><br>"
                           "- Check the GitHub repository for the latest releases and updates.<br>"
                           "- The application does not have an auto-update feature, so download the latest version manually from the repository if needed.<br><br>"
                           "<b>7.3 Notes</b><br>"
                           "- Support is provided on a volunteer basis by the developer and community.<br>"
                           "- Be patient when awaiting a response, especially for non-critical issues.",
                "japanese": "さらなる支援が必要な場合やバグを報告したい場合、このセクションではヘルプを得るために必要な情報を提供します。<br><br>"
                            "<b>7.1 GitHubリポジトリ</b><br>"
                            "- ケモノダウンローダーはGitHubでホストされているオープンソースプロジェクトです。<br>"
                            "- プロジェクトページをご覧ください：<a href='https://github.com/VoxDroid'>github.com/VoxDroid</a>。<br>"
                            "- 「Issues」タブで既存のバグ報告や機能リクエストを確認してください。問題がリストにない場合、以下の詳細を含めて新しいイシューを作成してください：<br>"
                            "  - 問題またはリクエストの明確な説明。<br>"
                            "  - 問題を再現する手順（該当する場合）。<br>"
                            "  - 関連するコンソールログやスクリーンショット。<br>"
                            "- 開発者のVoxDroidはリポジトリを監視し、時間があるときにイシューに応答します。<br><br>"
                            "<b>7.2 更新</b><br>"
                            "- GitHubリポジトリで最新のリリースと更新を確認してください。<br>"
                            "- アプリケーションには自動更新機能がないため、必要に応じてリポジトリから最新バージョンを手動でダウンロードしてください。<br><br>"
                            "<b>7.3 注意事項</b><br>"
                            "- サポートは開発者とコミュニティによるボランティアベースで提供されます。<br>"
                            "- 特に重要でない問題については、応答を待つ際に辛抱強くお待ちください。",
                "korean": "추가 지원이 필요하거나 버그를 보고하려면 이 섹션에서 도움을 받는 데 필요한 정보를 제공합니다.<br><br>"
                          "<b>7.1 GitHub 저장소</b><br>"
                          "- 케모노 다운로더는 GitHub에서 호스팅되는 오픈 소스 프로젝트입니다.<br>"
                          "- 프로젝트 페이지를 방문하세요: <a href='https://github.com/VoxDroid'>github.com/VoxDroid</a>.<br>"
                          "- 'Issues' 탭에서 기존 버그 보고서나 기능 요청을 확인하세요. 문제가 나열되지 않았다면 다음 세부 사항을 포함하여 새 이슈를 생성하세요:<br>"
                          "  - 문제 또는 요청에 대한 명확한 설명.<br>"
                          "  - 문제를 재현하는 단계(해당되는 경우).<br>"
                          "  - 관련 콘솔 로그 또는 스크린샷.<br>"
                          "- 개발자인 VoxDroid는 저장소를 모니터링하며 시간이 허락하는 한 이슈에 응답합니다.<br><br>"
                          "<b>7.2 업데이트</b><br>"
                          "- GitHub 저장소에서 최신 릴리스와 업데이트를 확인하세요.<br>"
                          "- 애플리케이션에는 자동 업데이트 기능이 없으므로 필요하면 저장소에서 최신 버전을 수동으로 다운로드하세요.<br><br>"
                          "<b>7.3 참고 사항</b><br>"
                          "- 지원은 개발자와 커뮤니티가 자원봉사로 제공합니다.<br>"
                          "- 특히 중요하지 않은 문제에 대한 응답을 기다릴 때는 인내심을 가지세요."
            }
        }
    
    def get_text(self, key, language=None, *args):
        """
        Get translated text for the given key.
        
        Args:
            key (str): The translation key
            language (str, optional): Language to use. If None, uses current_language
            *args: Format arguments to apply to the translated string
            
        Returns:
            str: Translated text
        """
        if language is None:
            language = self.current_language
            
        if key not in self.translations:
            return key
            
        if language not in self.translations[key]:
            language = "english"
            
        text = self.translations[key][language]
        
        if args:
            try:
                text = text.format(*args)
            except Exception:
                pass
                
        return text
    
    def set_language(self, language):
        """
        Set the current language.
        
        Args:
            language (str): Language to set ('english', 'japanese', 'korean', or 'chinese-simplified')
            
        Returns:
            bool: True if language was changed, False otherwise
        """
        if language not in ["english", "japanese", "korean", "chinese-simplified"]:
            return False
            
        if language != self.current_language:
            self.current_language = language
            return True
            
        return False
    
    def get_current_language(self):
        """
        Get the current language.
        
        Returns:
            str: Current language
        """
        return self.current_language
    
    def get_language_name(self, language=None):
        """
        Get the localized name of the specified language.
        
        Args:
            language (str, optional): Language to get name for. If None, uses current_language
            
        Returns:
            str: Localized language name
        """
        if language is None:
            language = self.current_language
            
        return self.get_text(language)
    
    def get_available_languages(self):
        """
        Get list of available languages.
        
        Returns:
            list: List of available languages
        """
        return ["english", "japanese", "korean", "chinese-simplified"]


language_manager = KDLanguage()


def translate(key, *args):
    """
    Convenience function to get translated text.
    
    Args:
        key (str): The translation key
        *args: Format arguments to apply to the translated string
        
    Returns:
        str: Translated text
    """
    return language_manager.get_text(key, None, *args)

