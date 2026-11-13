class KDLanguage:
    """
    Language management class for Kemono Downloader.
    Provides translations for all text in the application.
    Supports English (default), Japanese, Korean and Simplified Chinese.
    """

    def __init__(self):
        self.current_language = "english"  # Default language
        self.translations = {
            # Add links from txt file
            "add_links_from_file": {
                "english": "Add links from .txt file. Each link should be on a new line.",
                "japanese": ".txtファイルからリンクを追加します。各リンクは新しい行に配置してください。",
                "korean": ".txt 파일에서 링크를 추가합니다. 각 링크는 새 줄에 있어야 합니다.",
                "chinese-simplified": "从 .txt 文件添加链接。每个链接应位于新行上。",
            },
            "add_links_from_file_title": {
                "english": "Import from TXT File.",
                "japanese": "TXTファイルからインポート。",
                "korean": "TXT 파일에서 가져오기.",
                "chinese-simplified": "从 TXT 文件导入。",
            },
            "select_links_file": {
                "english": "Select .txt file containing creator URLs",
                "japanese": ".txtファイルからクリエイターのURLを含むファイルを選択してください",
                "korean": ".txt 파일에서 크리에이터 URL을 포함하는 파일을 선택하세요",
                "chinese-simplified": "选择包含创作者URL的.txt文件",
            },
            "select_tor_executable": {
                "english": "Select Tor executable",
                "japanese": "Tor実行ファイルを選択",
                "korean": "Tor 실행 파일 선택",
                "chinese-simplified": "选择Tor可执行文件",
            },
            "url_already_in_queue": {
                "english": "URL is already in the download queue",
                "japanese": "URLはすでにダウンロードキューにあります",
                "korean": "URL은 이미 다운로드 대기열에 있습니다",
                "chinese-simplified": "URL已在下载队列中",
            },
            "added_to_queue": {
                "english": "Added to queue",
                "japanese": "キューに追加されました",
                "korean": "대기열에 추가됨",
                "chinese-simplified": "已添加到队列",
            },
            "error": {
                "english": "Error",
                "japanese": "エラー",
                "korean": "오류",
                "chinese-simplified": "错误",
            },
            "invalid_url_format_from_txt": {
                "english": "Invalid URL format, skipping",
                "japanese": "無効なURL形式、スキップします",
                "korean": "잘못된 URL 형식, 건너뜁니다",
                "chinese-simplified": "无效的URL格式，跳过",
            },
            "error_processing_url": {
                "english": "Error processing URL",
                "japanese": "URL処理中にエラーが発生しました",
                "korean": "URL 처리 중 오류 발생",
                "chinese-simplified": "处理URL时出错",
            },
            "bulk_add_summary": {
                "english": "Added {0} link(s) to queue. Skipped {1} link(s).",
                "japanese": "キューに {0} 件のリンクを追加しました。{1} 件のリンクをスキップしました。",
                "korean": "대기열에 {0}개의 링크를 추가했습니다. {1}개의 링크를 건너뛰었습니다.",
                "chinese-simplified": "已将 {0} 个链接添加到队列。跳过了 {1} 个链接。",
            },
            "bulk_add_complete": {
                "english": "Bulk Add Complete",
                "japanese": "一括追加完了",
                "korean": "대량 추가 완료",
                "chinese-simplified": "批量添加完成",
            },
            "file_read_error": {
                "english": "Error reading file: {0}",
                "japanese": "ファイルの読み取りエラー：{0}",
                "korean": "파일 읽기 오류: {0}",
                "chinese-simplified": "读取文件时出错：{0}",
            },
            "file_read_error_title": {
                "english": "File Read Error",
                "japanese": "ファイル読み取りエラー",
                "korean": "파일 읽기 오류",
                "chinese-simplified": "文件读取错误",
            },
            # Log Texts
            "checking_creator_with_url": {
                "english": "Checking creator with URL: {0}",
                "japanese": "URL を使用してクリエイターを確認中: {0}",
                "korean": "URL로 크리에이터 확인 중: {0}",
                "chinese-simplified": "正在检查创作者，URL：{0}",
            },
            "parsed_url_service_creator": {
                "english": "Parsed URL - Service: {0}, Creator ID: {1}",
                "japanese": "解析したURL - サービス: {0}, クリエイターID: {1}",
                "korean": "URL 해석됨 - 서비스: {0}, 크리에이터 ID: {1}",
                "chinese-simplified": "已解析URL - 服务：{0}, 创作者ID：{1}",
            },
            "base_api_url": {
                "english": "Base API URL: {0}",
                "japanese": "ベースAPI URL: {0}",
                "korean": "기본 API URL: {0}",
                "chinese-simplified": "基础 API URL：{0}",
            },
            "successfully_validated_url": {
                "english": "Successfully validated URL {0}",
                "japanese": "URL {0} を正常に検証しました",
                "korean": "URL {0}을 성공적으로 검증했습니다",
                "chinese-simplified": "成功验证了URL {0}",
            },
            "thread_deleted_during_cancellation_wait": {
                "english": "A thread was deleted during cancellation wait",
                "japanese": "キャンセル待機中にスレッドが削除されました",
                "korean": "취소 대기 중 스레드가 삭제되었습니다",
                "chinese-simplified": "在取消等待期间，一个线程被删除了",
            },
            "thread_not_exited_gracefully": {
                "english": "Thread {0} did not exit gracefully, attempting termination.",
                "japanese": "スレッド {0} は正常に終了しませんでした。強制終了を試みます。",
                "korean": "스레드 {0} 가 정상적으로 종료되지 않았습니다. 강제 종료를 시도합니다.",
                "chinese-simplified": "线程 {0} 未正常退出，正在尝试终止。",
            },
            "creator_download_thread_started": {
                "english": "CreatorDownloadThread started for service: {0}, creator_id: {1}",
                "japanese": "サービス {0}、クリエイターID {1} のためにCreatorDownloadThreadを開始しました",
                "korean": "서비스 {0}, 크리에이터 ID {1}에 대해 CreatorDownloadThread를 시작했습니다",
                "chinese-simplified": "为服务 {0}，创建者ID {1} 启动了CreatorDownloadThread",
            },
            "total_posts": {
                "english": "Total posts: {0}",
                "japanese": "投稿の合計：{0}",
                "korean": "총 게시물 수: {0}",
                "chinese-simplified": "帖子总数：{0}",
            },
            "failed_to_create_creator_folder": {
                "english": "Failed to create creator folder {0}: {1}",
                "japanese": "クリエイターフォルダ {0} の作成に失敗しました：{1}",
                "korean": "크리에이터 폴더 {0} 생성에 실패했습니다: {1}",
                "chinese-simplified": "无法创建创建者文件夹 {0}：{1}",
            },
            "created_directory": {
                "english": "Created directory: {0}",
                "japanese": "ディレクトリを作成しました：{0}",
                "korean": "디렉토리를 생성했습니다: {0}",
                "chinese-simplified": "已创建目录：{0}",
            },
            "total_selected_files_to_download": {
                "english": "Total selected files to download: {0}",
                "japanese": "ダウンロードする選択済みファイルの合計：{0}",
                "korean": "다운로드할 선택된 총 파일 수: {0}",
                "chinese-simplified": "选择的要下载的文件总数：{0}",
            },
            "error_in_async_download_loop": {
                "english": "Error in async download loop: {0}",
                "japanese": "非同期ダウンロードループでのエラー：{0}",
                "korean": "비동기 다운로드 루프에서 오류: {0}",
                "chinese-simplified": "异步下载循环错误：{0}",
            },
            "no_files_selected_for_download": {
                "english": "No files selected for download.",
                "japanese": "ダウンロードするファイルが選択されていません。",
                "korean": "다운로드할 파일이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的文件。",
            },
            "failed_to_download_file": {
                "english": "Failed to download {0}: {1}",
                "japanese": "{0} のダウンロードに失敗しました：{1}",
                "korean": "{0} 다운로드에 실패했습니다: {1}",
                "chinese-simplified": "无法下载 {0}：{1}",
            },
            "checking_main_file": {
                "english": "Checking main file: {0} ({1})",
                "japanese": "メインファイルを確認中：{0}（{1}）",
                "korean": "메인 파일 확인 중: {0} ({1})",
                "chinese-simplified": "正在检查主文件：{0}（{1}）",
            },
            "added_main_file": {
                "english": "Added main file: {0}",
                "japanese": "メインファイルを追加しました：{0}",
                "korean": "메인 파일을 추가했습니다: {0}",
                "chinese-simplified": "已添加主文件：{0}",
            },
            "checking_attachment": {
                "english": "Checking attachment: {0} ({1})",
                "japanese": "添付ファイルを確認中：{0}（{1}）",
                "korean": "첨부 파일 확인 중: {0} ({1})",
                "chinese-simplified": "正在检查附件：{0}（{1}）",
            },
            "added_attachment": {
                "english": "Added attachment: {0}",
                "japanese": "添付ファイルを追加しました：{0}",
                "korean": "첨부 파일을 추가했습니다: {0}",
                "chinese-simplified": "已添加附件：{0}",
            },
            "detecting_files_for_post": {
                "english": "Detecting files for post with allowed extensions: {0}",
                "japanese": "許可された拡張子で投稿のファイルを検出中：{0}",
                "korean": "허용된 확장자로 게시물의 파일을 감지 중: {0}",
                "chinese-simplified": "正在检测具有允许扩展名的帖子文件：{0}",
            },
            "thread_already_deleted_during_termination": {
                "english": "Thread {0} already deleted during termination",
                "japanese": "スレッド {0} は終了処理中にすでに削除されています",
                "korean": "스레드 {0} 는 종료 처리 중 이미 삭제되었습니다",
                "chinese-simplified": "线程 {0} 在终止过程中已被删除",
            },
            "cancellation_process_completed": {
                "english": "Cancellation process completed",
                "japanese": "キャンセル処理が完了しました",
                "korean": "취소 프로세스가 완료되었습니다",
                "chinese-simplified": "取消过程已完成",
            },
            "checkbox_toggle_finished": {
                "english": "Checkbox toggle finished, checked posts: {0}, visible posts: {1}",
                "japanese": "チェックボックスの切り替えが完了しました。チェックされた投稿: {0}, 表示された投稿: {1}",
                "korean": "체크박스 전환이 완료되었습니다. 선택된 게시물: {0}, 표시된 게시물: {1}",
                "chinese-simplified": "复选框切换完成，已选帖子：{0}, 可见帖子：{1}",
            },
            "no_current_creator_url_set": {
                "english": "No current creator URL set.",
                "japanese": "現在のクリエイターURLが設定されていません。",
                "korean": "현재 제작자 URL이 설정되지 않았습니다.",
                "chinese-simplified": "未设置当前创作者 URL。",
            },
            "no_posts_selected_for_creator": {
                "english": "No posts selected for {0}. Checked URLs: {1}",
                "japanese": "{0} に対して投稿が選択されていません。確認済みURL: {1}",
                "korean": "{0}에 대해 선택된 게시물이 없습니다. 확인된 URL: {1}",
                "chinese-simplified": "未为 {0} 选择任何帖子。已检查的 URL：{1}",
            },
            "no_visible_posts_to_toggle": {
                "english": "No visible posts to toggle.",
                "japanese": "切り替える表示可能な投稿がありません。",
                "korean": "전환할 수 있는 표시된 게시물이 없습니다.",
                "chinese-simplified": "没有可切换的可见帖子。",
            },
            "no_posts_to_toggle": {
                "english": "No posts to toggle.",
                "japanese": "切り替える投稿がありません。",
                "korean": "전환할 게시물이 없습니다.",
                "chinese-simplified": "没有可切换的帖子。",
            },
            "download_completed_with_failed_files": {
                "english": "Download completed with {0} failed files:",
                "japanese": "ダウンロードが完了しましたが、{0} 件のファイルが失敗しました:",
                "korean": "다운로드가 완료되었지만 {0}개의 파일이 실패했습니다:",
                "chinese-simplified": "下载完成，但有 {0} 个文件失败：",
            },
            "download_file_failed_with_error": {
                "english": "Failed to download {0}: {1}",
                "japanese": "{0} のダウンロードに失敗しました: {1}",
                "korean": "{0} 다운로드 실패: {1}",
                "chinese-simplified": "下载 {0} 失败：{1}",
            },
            "checkbox_toggle_already_in_progress": {
                "english": "Checkbox toggle already in progress. Please wait.",
                "japanese": "チェックボックスの切り替えはすでに進行中です。しばらくお待ちください。",
                "korean": "체크박스 전환이 이미 진행 중입니다. 잠시만 기다려 주세요.",
                "chinese-simplified": "复选框切换已在进行中。请稍候。",
            },
            "all_posts_and_files_completed": {
                "english": "All posts and files completed for current creator.",
                "japanese": "現在のクリエイターのすべての投稿とファイルが完了しました。",
                "korean": "현재 제작자의 모든 게시물과 파일이 완료되었습니다.",
                "chinese-simplified": "当前创作者的所有帖子和文件已完成。",
            },
            "overall_progress_updated": {
                "english": "Overall progress updated: {0}/{1} files, {2}%",
                "japanese": "全体の進捗が更新されました: {0}/{1} ファイル, {2}%",
                "korean": "전체 진행 상황이 업데이트되었습니다: {0}/{1} 파일, {2}%",
                "chinese-simplified": "总体进度已更新：{0}/{1} 个文件，{2}%",
            },
            "filtering_already_in_progress": {
                "english": "Filtering already in progress. Please wait.",
                "japanese": "フィルタリングはすでに進行中です。しばらくお待ちください。",
                "korean": "필터링이 이미 진행 중입니다. 잠시만 기다려 주세요.",
                "chinese-simplified": "筛选已在进行中。请稍候。",
            },
            "filtering_completed_displayed_posts": {
                "english": "Filtering completed, displayed {0} posts",
                "japanese": "フィルタリングが完了しました。表示された投稿数: {0}",
                "korean": "필터링이 완료되었습니다. 표시된 게시물: {0}",
                "chinese-simplified": "筛选完成，显示了 {0} 个帖子",
            },
            "displayed_page_posts": {
                "english": "Displayed page {0} with {1} posts",
                "japanese": "ページ {0} を表示（投稿数: {1}）",
                "korean": "페이지 {0} 표시（게시물: {1}）",
                "chinese-simplified": "显示第 {0} 页（{1} 个帖子）",
            },
            "no_post_id_found_for_title": {
                "english": "No post ID found for title: {0}",
                "japanese": "タイトルに対応する投稿IDが見つかりません: {0}",
                "korean": "제목에 대한 게시물 ID를 찾을 수 없습니다: {0}",
                "chinese-simplified": "未找到标题对应的帖子 ID：{0}",
            },
            "updated_checked_posts_count": {
                "english": "Updated checked posts count: {0}, checked_urls: {1}, all_detected: {2}, selected IDs: {3}",
                "japanese": "チェック済み投稿数を更新しました: {0}, 確認済みURL: {1}, 検出された全件: {2}, 選択されたID: {3}",
                "korean": "체크된 게시물 수가 업데이트되었습니다: {0}, 확인된 URL: {1}, 감지된 전체: {2}, 선택된 ID: {3}",
                "chinese-simplified": "已更新已检查帖子数：{0}, 已检查 URL：{1}, 检测到的总数：{2}, 已选择的 ID：{3}",
            },
            "trying_endpoint": {
                "english": "Trying endpoint: {0}",
                "japanese": "エンドポイントを試しています: {0}",
                "korean": "엔드포인트 시도 중: {0}",
                "chinese-simplified": "正在尝试端点：{0}",
            },
            "reached_last_page": {
                "english": "Reached last page for creator {0}. Total posts fetched: {1}",
                "japanese": "クリエイター {0} の最後のページに到達しました。取得した投稿の合計：{1}",
                "korean": "크리에이터 {0}의 마지막 페이지에 도달했습니다. 가져온 총 게시물 수: {1}",
                "chinese-simplified": "已到达创建者 {0} 的最后一页。获取的帖子总数：{1}",
            },
            "all_api_endpoints_failed": {
                "english": "All API endpoints failed for creator {0}",
                "japanese": "クリエイター {0} のすべてのAPIエンドポイントが失敗しました",
                "korean": "크리에이터 {0}의 모든 API 엔드포인트가 실패했습니다",
                "chinese-simplified": "创建者 {0} 的所有API端点均失败",
            },
            "successfully_decompressed_gzipped_response": {
                "english": "Successfully decompressed gzipped response",
                "japanese": "gzipped応答の解凍に成功しました",
                "korean": "gzipped 응답을 성공적으로 압축 해제했습니다",
                "chinese-simplified": "成功解压gzipped响应",
            },
            "gzip_decompression_failed": {
                "english": "Gzip decompression failed, trying plain text: {0}",
                "japanese": "Gzip解凍に失敗しました、プレーンテキストを試みます：{0}",
                "korean": "Gzip 압축 해제에 실패했습니다, 일반 텍스트를 시도합니다: {0}",
                "chinese-simplified": "Gzip解压失败，尝试纯文本：{0}",
            },
            "empty_response_at_offset": {
                "english": "Empty response at offset {0}. No more posts available.",
                "japanese": "オフセット {0} で空の応答。投稿がこれ以上ありません。",
                "korean": "오프셋 {0}에서 빈 응답. 더 이상 게시물이 없습니다.",
                "chinese-simplified": "在偏移量 {0} 处收到空响应。没有更多帖子可用。",
            },
            "failed_to_parse_response": {
                "english": "Failed to parse response: {0}",
                "japanese": "応答の解析に失敗しました：{0}",
                "korean": "응답 파싱에 실패했습니다: {0}",
                "chinese-simplified": "解析响应失败：{0}",
            },
            "response_content_first_500_chars": {
                "english": "Response content (first 500 chars): {0}",
                "japanese": "応答内容（最初の500文字）：{0}",
                "korean": "응답 내용 (처음 500자): {0}",
                "chinese-simplified": "响应内容（前500个字符）：{0}",
            },
            "using_cached_posts_fallback": {
                "english": "Fetching failed, using cached posts for {0}",
                "japanese": "取得に失敗しました、{0}のキャッシュされた投稿を使用します",
                "korean": "가져오기에 실패하여 {0}의 캐시된 게시물을 사용합니다",
                "chinese-simplified": "获取失败，使用 {0} 的缓存帖子",
            },
            "endpoint_successful": {
                "english": "Endpoint successful: {0}",
                "japanese": "エンドポイントに成功しました: {0}",
                "korean": "엔드포인트 성공: {0}",
                "chinese-simplified": "端点成功：{0}",
            },
            "endpoint_returned_status_likely_end": {
                "english": "Endpoint returned {0} (likely reached end of data): {1}",
                "japanese": "エンドポイントが {0} を返しました（データの終端に到達した可能性あり）: {1}",
                "korean": "엔드포인트가 {0}을(를) 반환했습니다 (데이터 끝에 도달했을 가능성 있음): {1}",
                "chinese-simplified": "端点返回 {0}（可能已到达数据末尾）：{1}",
            },
            "endpoint_failed_with_status": {
                "english": "Endpoint failed: {0} - Status: {1}",
                "japanese": "エンドポイントに失敗しました: {0} - ステータス: {1}",
                "korean": "엔드포인트 실패: {0} - 상태: {1}",
                "chinese-simplified": "端点失败：{0} - 状态：{1}",
            },
            "endpoint_unavailable_likely_end": {
                "english": "Endpoint unavailable (likely reached end of data): {0} - {1}",
                "japanese": "エンドポイントが利用できません（データの終端に到達した可能性あり）: {0} - {1}",
                "korean": "엔드포인트를 사용할 수 없습니다 (데이터 끝에 도달했을 가능성 있음): {0} - {1}",
                "chinese-simplified": "端点不可用（可能已到达数据末尾）：{0} - {1}",
            },
            "endpoint_error_with_exception": {
                "english": "Endpoint error: {0} - {1}",
                "japanese": "エンドポイントエラー: {0} - {1}",
                "korean": "엔드포인트 오류: {0} - {1}",
                "chinese-simplified": "端点错误：{0} - {1}",
            },
            "validation_attempt_failed": {
                "english": "Validation attempt {0} failed, retrying in {1}s...",
                "japanese": "検証試行 {0} が失敗しました、{1}秒後に再試行します...",
                "korean": "검증 시도 {0}이 실패했습니다, {1}초 후에 재시도합니다...",
                "chinese-simplified": "验证尝试 {0} 失败，将在 {1}秒后重试...",
            },
            "unexpected_response_structure": {
                "english": "Unexpected response structure: {0}",
                "japanese": "予期しない応答構造：{0}",
                "korean": "예상치 못한 응답 구조: {0}",
                "chinese-simplified": "意外的响应结构：{0}",
            },
            "invalid_posts_data_type": {
                "english": "Invalid posts data type: {0}",
                "japanese": "無効な投稿データ型：{0}",
                "korean": "잘못된 게시물 데이터 유형: {0}",
                "chinese-simplified": "无效的帖子数据类型：{0}",
            },
            "no_more_posts_at_offset": {
                "english": "No more posts to fetch at offset {0}. Stopping pagination.",
                "japanese": "オフセット {0} で取得する投稿がありません。ページネーションを停止します。",
                "korean": "오프셋 {0}에서 가져올 게시물이 없습니다. 페이지네이션을 중지합니다.",
                "chinese-simplified": "在偏移量 {0} 处没有更多帖子可获取。停止分页。",
            },
            "last_page_reached_with_counts": {
                "english": "Last page reached (received {0} posts, expected {1}). Total posts fetched: {2}",
                "japanese": "最後のページに到達しました（{0} 件の投稿を受信、{1} 件を期待）。取得した投稿の合計：{2}",
                "korean": "마지막 페이지에 도달했습니다 ({0}개의 게시물 수신, {1}개 예상). 가져온 총 게시물 수: {2}",
                "chinese-simplified": "已到达最后一页（收到 {0} 个帖子，预期 {1} 个）。获取的帖子总数：{2}",
            },
            "prepared_posts_for_population": {
                "english": "Prepared {0} posts for population, unique titles: {1}",
                "japanese": "{0} 件の投稿を入力用に準備しました、ユニークなタイトル数：{1}",
                "korean": "{0}개의 게시물을 채우기 위해 준비했습니다, 고유 제목 수: {1}",
                "chinese-simplified": "为填充准备了 {0} 个帖子，唯一标题数：{1}",
            },
            "total_posts_fetched_for_creator": {
                "english": "Total posts fetched for creator {0}: {1}",
                "japanese": "クリエイター {0} のために取得した投稿の合計：{1}",
                "korean": "크리에이터 {0}에 대해 가져온 총 게시물 수: {1}",
                "chinese-simplified": "为创建者 {0} 获取的帖子总数：{1}",
            },
            "checking_content_image": {
                "english": "Checking content image: {0} ({1})",
                "japanese": "コンテンツ画像を確認中：{0}（{1}）",
                "korean": "콘텐츠 이미지 확인 중: {0} ({1})",
                "chinese-simplified": "正在检查内容图像：{0}（{1}）",
            },
            "added_content_image": {
                "english": "Added content image: {0}",
                "japanese": "コンテンツ画像を追加しました：{0}",
                "korean": "콘텐츠 이미지를 추가했습니다: {0}",
                "chinese-simplified": "已添加内容图像：{0}",
            },
            "total_files_detected": {
                "english": "Total files detected: {0}",
                "japanese": "検出されたファイルの合計：{0}",
                "korean": "감지된 총 파일 수: {0}",
                "chinese-simplified": "检测到的文件总数：{0}",
            },
            "total_files_to_download": {
                "english": "Total files to download: {0}",
                "japanese": "ダウンロードするファイルの合計：{0}",
                "korean": "다운로드할 총 파일 수: {0}",
                "chinese-simplified": "要下载的文件总数：{0}",
            },
            "failed_to_fetch_creator_name": {
                "english": "Failed to fetch creator name, using default: {0}",
                "japanese": "クリエイター名の取得に失敗しました、デフォルトを使用：{0}",
                "korean": "크리에이터 이름을 가져오지 못했습니다, 기본값 사용: {0}",
                "chinese-simplified": "无法获取创建者名称，使用默认值：{0}",
            },
            "error_fetching_creator_name": {
                "english": "Error fetching creator name: {0}",
                "japanese": "クリエイター名の取得エラー：{0}",
                "korean": "크리에이터 이름 가져오기 오류: {0}",
                "chinese-simplified": "获取创建者名称出错：{0}",
            },
            "fetched_title_for_post": {
                "english": "Fetched title for post {0}: {1}",
                "japanese": "投稿 {0} のタイトルを取得しました：{1}",
                "korean": "게시물 {0}의 제목을 가져왔습니다: {1}",
                "chinese-simplified": "获取了帖子 {0} 的标题：{1}",
            },
            "failed_to_fetch_title_for_post": {
                "english": "Failed to fetch title for post {0}, using default",
                "japanese": "投稿 {0} のタイトル取得に失敗しました、デフォルトを使用",
                "korean": "게시물 {0}의 제목을 가져오지 못했습니다, 기본값 사용",
                "chinese-simplified": "无法获取帖子 {0} 的标题，使用默认值",
            },
            "error_fetching_title_for_post": {
                "english": "Error fetching title for post {0}: {1}",
                "japanese": "投稿 {0} のタイトル取得エラー：{1}",
                "korean": "게시물 {0}의 제목 가져오기 오류: {1}",
                "chinese-simplified": "获取帖子 {0} 的标题出错：{1}",
            },
            "failed_to_create_post_folder": {
                "english": "Failed to create post folder {0}: {1}. Likely due to invalid folder name.",
                "japanese": "投稿フォルダ {0} の作成に失敗しました：{1}。フォルダ名が無効な可能性があります。",
                "korean": "게시물 폴더 {0} 생성에 실패했습니다: {1}. 폴더 이름이 유효하지 않을 가능성이 있습니다.",
                "chinese-simplified": "无法创建帖子文件夹 {0}：{1}。可能是由于文件夹名称无效。",
            },
            "unexpected_error_downloading": {
                "english": "Unexpected error downloading {0}: {1}",
                "japanese": "{0} のダウンロード中に予期しないエラー：{1}",
                "korean": "{0} 다운로드 중 예기치 않은 오류: {1}",
                "chinese-simplified": "下载 {0} 时发生意外错误：{1}",
            },
            "error_in_download_worker": {
                "english": "Error in download worker: {0}",
                "japanese": "ダウンロードワーカーでのエラー：{0}",
                "korean": "다운로드 작업자 오류: {0}",
                "chinese-simplified": "下载工作进程错误：{0}",
            },
            "rate_limit_hit": {
                "english": "Rate limit hit for {0} (attempt {1}/{2}). Retrying...",
                "japanese": "{0} のレート制限に達しました（試行 {1}/{2}）。再試行中...",
                "korean": "{0}에 대한 속도 제한에 도달했습니다 (시도 {1}/{2}). 재시도 중...",
                "chinese-simplified": "{0} 的速率限制已达到（尝试 {1}/{2}）。正在重试...",
            },
            "failed_to_fetch_api": {
                "english": "Failed to fetch {0} - Status code: {1}",
                "japanese": "{0} の取得に失敗しました - ステータスコード：{1}",
                "korean": "{0} 가져오기에 실패했습니다 - 상태 코드: {1}",
                "chinese-simplified": "无法获取 {0} - 状态码：{1}",
            },
            "error_fetching_post_max_attempts": {
                "english": "Error fetching post {0} after {1} attempts: {2}",
                "japanese": "投稿 {0} の取得エラー、{1} 回試行後：{2}",
                "korean": "게시물 {0} 가져오기 오류, {1}번 시도 후: {2}",
                "chinese-simplified": "获取帖子 {0} 出错，经过 {1} 次尝试：{2}",
            },
            "error_fetching_post": {
                "english": "Error fetching post {0} (attempt {1}/{2}): {3}. Retrying...",
                "japanese": "投稿 {0} の取得エラー（試行 {1}/{2}）：{3}。再試行中...",
                "korean": "게시물 {0} 가져오기 오류 (시도 {1}/{2}): {3}. 재시도 중...",
                "chinese-simplified": "获取帖子 {0} 出错（尝试 {1}/{2}）：{3}。正在重试...",
            },
            "trying_again_in": {
                "english": "Trying again in {0}",
                "japanese": "{0}秒後に再試行します",
                "korean": "{0}초 후에 다시 시도합니다",
                "chinese-simplified": "{0}秒后再次尝试",
            },
            "allowed_extensions_for_download": {
                "english": "Allowed extensions for download: {0}",
                "japanese": "ダウンロードの許可された拡張子：{0}",
                "korean": "다운로드 허용된 확장자: {0}",
                "chinese-simplified": "允许下载的扩展名：{0}",
            },
            "no_matching_creator_urls": {
                "english": "No matching creator URLs found for selected posts.",
                "japanese": "選択した投稿に対応するクリエイターのURLが見つかりませんでした。",
                "korean": "선택한 게시물에 대해 일치하는 크리에이터 URL을 찾을 수 없습니다.",
                "chinese-simplified": "未找到与所选帖子匹配的创建者URL。",
            },
            "fetched_posts_at_offset": {
                "english": "Fetched {0} posts at offset {1}",
                "japanese": "オフセット {1} で {0} 件の投稿を取得しました",
                "korean": "오프셋 {1}에서 {0}개의 게시물을 가져왔습니다",
                "chinese-simplified": "在偏移量 {1} 处获取了 {0} 个帖子",
            },
            "received_less_than_page_size": {
                "english": "Received {0} posts (less than page size {1}), indicating last page reached",
                "japanese": "{0} 件の投稿を受信しました（ページサイズ {1} 未満）、最後のページに到達したことを示します",
                "korean": "{0}개의 게시물을 수신했습니다 (페이지 크기 {1} 미만), 마지막 페이지에 도달했음을 나타냅니다",
                "chinese-simplified": "接收到 {0} 个帖子（少于页面大小 {1}），表明已到达最后一页",
            },
            "post_id_and_title": {
                "english": "Post ID: {0}, Title: {1}",
                "japanese": "投稿ID：{0}、タイトル：{1}",
                "korean": "게시물 ID: {0}, 제목: {1}",
                "chinese-simplified": "帖子ID：{0}，标题：{1}",
            },
            "network_error_attempt": {
                "english": "Network error on attempt {0}: {1}, retrying...",
                "japanese": "試行 {0} でネットワークエラー：{1}、再試行中...",
                "korean": "시도 {0}에서 네트워크 오류: {1}, 재시도 중...",
                "chinese-simplified": "尝试 {0} 时网络错误：{1}，正在重试...",
            },
            "failed_to_validate": {
                "english": "Failed to validate {0} after {1} attempts: {2}",
                "japanese": "{0} の検証に {1} 回試行後失敗しました：{2}",
                "korean": "{0} 검증이 {1}번 시도 후 실패했습니다: {2}",
                "chinese-simplified": "在 {1} 次尝试后无法验证 {0}：{2}",
            },
            "validation_in_progress": {
                "english": "Validation already in progress. Please wait.",
                "japanese": "検証がすでに進行中です。しばらくお待ちください。",
                "korean": "검증이 이미 진행 중입니다. 잠시 기다려 주세요.",
                "chinese-simplified": "验证已在进行中。请稍等。",
            },
            "checkbox_toggled_for_post": {
                "english": "Checkbox toggled for post {0} (ID: {1}) to {2}",
                "japanese": "投稿 {0} (ID: {1}) のチェックボックスが {2} に切り替えられました",
                "korean": "게시물 {0} (ID: {1})의 체크박스가 {2}(으)로 전환되었습니다",
                "chinese-simplified": "帖子 {0} (ID: {1}) 的复选框已切换为 {2}",
            },
            "check_all_state_updated": {
                "english": "Check ALL state updated to {0}",
                "japanese": "すべてをチェック状態が {0} に更新されました",
                "korean": "모두 선택 상태가 {0}(으)로 업데이트되었습니다",
                "chinese-simplified": "全选状态已更新为 {0}",
            },
            "viewing_not_supported_for_url": {
                "english": "Viewing not supported for {0}",
                "japanese": "{0} の表示はサポートされていません",
                "korean": "{0} 보기 기능은 지원되지 않습니다",
                "chinese-simplified": "不支持查看 {0}",
            },
            "starting_cancellation_of_active_threads": {
                "english": "Starting cancellation of active threads",
                "japanese": "アクティブスレッドのキャンセルを開始します",
                "korean": "활성 스레드 취소를 시작합니다",
                "chinese-simplified": "开始取消活动线程",
            },
            "signaled_stop_for_thread": {
                "english": "Signaled stop for thread {0}",
                "japanese": "スレッド {0} に停止シグナルを送信しました",
                "korean": "스레드 {0}에 정지 신호를 보냈습니다",
                "chinese-simplified": "已向线程 {0} 发送停止信号",
            },
            "thread_already_deleted": {
                "english": "Thread {0} already deleted",
                "japanese": "スレッド {0} はすでに削除されています",
                "korean": "스레드 {0} 는 이미 삭제되었습니다",
                "chinese-simplified": "线程 {0} 已被删除",
            },
            "checkbox_toggle_completed": {
                "english": "Checkbox toggle completed: Check ALL = {0}, Affected posts: {1}, Total checked: {2}",
                "japanese": "チェックボックスの切り替えが完了しました：すべてチェック = {0}、影響を受けた投稿：{1}、合計チェック数：{2}",
                "korean": "체크박스 토글 완료: 모두 체크 = {0}, 영향을 받은 게시물: {1}, 총 체크 수: {2}",
                "chinese-simplified": "复选框切换完成：全部选中 = {0}，受影响的帖子：{1}，总计选中：{2}",
            },
            "post_detection_in_progress": {
                "english": "Post detection already in progress. Please wait.",
                "japanese": "投稿検出がすでに進行中です。しばらくお待ちください。",
                "korean": "게시물 감지가 이미 진행 중입니다. 잠시 기다려 주세요。",
                "chinese-simplified": "帖子检测已在进行中。请稍等。",
            },
            "populated_posts_for_creator": {
                "english": "Populated {0} posts for creator {1}",
                "japanese": "クリエイター {1} のために {0} 件の投稿を入力しました",
                "korean": "크리에이터 {1}을 위해 {0}개의 게시물을 채웠습니다",
                "chinese-simplified": "为创建者 {1} 填充了 {0} 个帖子",
            },
            "no_creator_viewed": {
                "english": "No creator currently viewed to download.",
                "japanese": "現在ダウンロードするクリエイターが表示されていません。",
                "korean": "현재 다운로드할 크리에이터가 없습니다.",
                "chinese-simplified": "当前没有查看的创建者可供下载。",
            },
            "posts_to_download_num": {
                "english": "Posts to download: {0}",
                "japanese": "ダウンロードする投稿数：{0}",
                "korean": "다운로드할 게시물 수: {0}",
                "chinese-simplified": "要下载的帖子数：{0}",
            },
            "file_preparation_in_progress": {
                "english": "File preparation already in progress. Please wait.",
                "japanese": "ファイルの準備がすでに進行中です。しばらくお待ちください。",
                "korean": "파일 준비가 이미 진행 중입니다. 잠시 기다려 주세요。",
                "chinese-simplified": "文件准备已在进行中。请稍等。",
            },
            "post_id_mismatch": {
                "english": "Post ID mismatch: Expected {0}, got {1}",
                "japanese": "投稿IDの不一致：期待値 {0}、取得値 {1}",
                "korean": "게시물 ID 불일치: 기대값 {0}, 실제값 {1}",
                "chinese-simplified": "帖子ID不匹配：预期 {0}，实际 {1}",
            },
            "no_posts_available": {
                "english": "No posts available for download. Skipping.",
                "japanese": "ダウンロード可能な投稿がありません。スキップします。",
                "korean": "다운로드할 수 있는 게시물이 없습니다. 건너뜁니다.",
                "chinese-simplified": "没有可下载的帖子。跳过。",
            },
            "detected_file": {
                "english": "Detected file: {0} from {1}",
                "japanese": "検出されたファイル：{0}（{1} から）",
                "korean": "감지된 파일: {0} ({1}에서)",
                "chinese-simplified": "检测到的文件：{0}（来自 {1}）",
            },
            "no_files_detected": {
                "english": "No files detected for selected posts. Skipping.",
                "japanese": "選択した投稿にファイルが検出されませんでした。スキップします。",
                "korean": "선택한 게시물에 파일이 감지되지 않았습니다. 건너뜁니다。",
                "chinese-simplified": "未检测到所选帖子的文件。跳过。",
            },
            "prepared_files_for_download": {
                "english": "Prepared {0} files for download",
                "japanese": "{0} 件のファイルをダウンロード用に準備しました",
                "korean": "{0}개의 파일을 다운로드 준비했습니다",
                "chinese-simplified": "为下载准备了 {0} 个文件",
            },
            "file_completed": {
                "english": "File completed: {0}, Total completed: {1}/{2}",
                "japanese": "ファイル完了: {0}, 完了合計: {1}/{2}",
                "korean": "파일 완료: {0}, 총 완료: {1}/{2}",
                "chinese-simplified": "文件完成：{0}, 已完成总数：{1}/{2}",
            },
            "file_failed": {
                "english": "File failed: {0}, Total failed: {1}",
                "japanese": "ファイル失敗: {0}, 失敗合計: {1}",
                "korean": "파일 실패: {0}, 총 실패: {1}",
                "chinese-simplified": "文件失败：{0}, 失败总数：{1}",
            },
            "all_files_attempted": {
                "english": "All files attempted (successful or failed), triggering download finished",
                "japanese": "すべてのファイルを試行しました（成功または失敗）、ダウンロード完了をトリガーします",
                "korean": "모든 파일을 시도했습니다(성공 또는 실패), 다운로드 완료를 트리거합니다",
                "chinese-simplified": "所有文件已尝试（成功或失败），触发下载完成",
            },
            "moving_to_next_creator": {
                "english": "Moving to next creator: {0}",
                "japanese": "次のクリエイターに移ります：{0}",
                "korean": "다음 크리에이터로 이동: {0}",
                "chinese-simplified": "移动到下一个创建者：{0}",
            },
            "terminated_lingering_thread": {
                "english": "Terminated lingering thread: {0}",
                "japanese": "残留スレッドを終了しました：{0}",
                "korean": "잔류 스레드를 종료했습니다: {0}",
                "chinese-simplified": "终止了残留线程：{0}",
            },
            "waiting_for_remaining_files": {
                "english": "Waiting for remaining files: {0}/{1}, Failed: {2}, Active threads: {3}",
                "japanese": "残りのファイルを待機中: {0}/{1}, 失敗: {2}, アクティブスレッド: {3}",
                "korean": "남은 파일을 기다리는 중: {0}/{1}, 실패: {2}, 활성 스레드: {3}",
                "chinese-simplified": "正在等待剩余文件：{0}/{1}, 失败：{2}, 活动线程：{3}",
            },
            "no_active_downloads_to_cancel": {
                "english": "No active downloads to cancel",
                "japanese": "キャンセルするアクティブなダウンロードはありません",
                "korean": "취소할 활성 다운로드가 없습니다",
                "chinese-simplified": "没有可取消的活动下载",
            },
            "deleting_thread": {
                "english": "Deleting thread {0}",
                "japanese": "スレッド {0} を削除中",
                "korean": "스레드 {0} 삭제 중",
                "chinese-simplified": "正在删除线程 {0}",
            },
            "no_more_active_threads": {
                "english": "No more active threads or creators. Finishing.",
                "japanese": "これ以上アクティブなスレッドや作成者はありません。終了します。",
                "korean": "더 이상 활성 스레드나 생성자가 없습니다. 종료합니다.",
                "chinese-simplified": "没有更多活动的线程或创建者。正在结束。",
            },
            "completed": {
                "english": "Completed",
                "japanese": "完了",
                "korean": "완료",
                "chinese-simplified": "已完成",
            },
            "failed": {
                "english": "Failed",
                "japanese": "失敗",
                "korean": "실패",
                "chinese-simplified": "失败",
            },
            "auto_rename": {
                "english": "Auto Rename and sort File name by order",
                "japanese": "自動リネームとファイル名を順序で並べ替え",
                "korean": "자동 이름 바꾸기 및 순서별 파일 이름 정렬",
                "chinese-simplified": "自动重命名并按顺序排序文件名",
            },
            "creator_downloader_settings": {
                "english": "Creator Downloader",
                "japanese": "クリエイターダウンローダー設定",
                "korean": "크리에이터 다운로더 설정",
                "chinese-simplified": "创作者下载器 设置",
            },
            "filename_template": {
                "english": "Filename Template",
                "japanese": "ファイル名テンプレート",
                "korean": "파일 이름 템플릿",
                "chinese-simplified": "文件名模板",
            },
            "tmpl_postid_orig": {
                "english": "{post_id}_{orig_name}",
                "japanese": "{post_id}_{orig_name}",
                "korean": "{post_id}_{orig_name}",
                "chinese-simplified": "{post_id}_{orig_name}",
            },
            "tmpl_posttitle_postid_orig": {
                "english": "{post_title}-{post_id}-{orig_name}",
                "japanese": "{post_title}-{post_id}-{orig_name}",
                "korean": "{post_title}-{post_id}-{orig_name}",
                "chinese-simplified": "{post_title}-{post_id}-{orig_name}",
            },
            "tmpl_postid_posttitle": {
                "english": "{post_id}_{post_title}",
                "japanese": "{post_id}_{post_title}",
                "korean": "{post_id}_{post_title}",
                "chinese-simplified": "{post_id}_{post_title}",
            },
            "tmpl_index_posttitle": {
                "english": "{file_index}_{post_title}_{orig_name}",
                "japanese": "{file_index}_{post_title}_{orig_name}",
                "korean": "{file_index}_{post_title}_{orig_name}",
                "chinese-simplified": "{file_index}_{post_title}_{orig_name}",
            },
            "tmpl_custom": {
                "english": "Custom...",
                "japanese": "カスタム...",
                "korean": "사용자 정의...",
                "chinese-simplified": "自定义...",
            },
            "filename_template_help_title": {
                "english": "Filename Template Help",
                "japanese": "ファイル名テンプレートヘルプ",
                "korean": "파일 이름 템플릿 도움말",
                "chinese-simplified": "文件名模板 帮助",
            },
            "filename_template_help_text": {
                "english": "You can use placeholders in templates:\n{post_title}, {post_id}, {orig_name}, {ext}, {creator_name}, {creator_id}, {file_index}, {total_files}\nExample: {post_title}-{post_id}-{orig_name}.\nIf a template errors, the fallback {post_id}_{orig_name} will be used.",
                "japanese": "テンプレートではプレースホルダを使用できます:\n{post_title}, {post_id}, {orig_name}, {ext}, {creator_name}, {creator_id}, {file_index}, {total_files}\n例: {post_title}-{post_id}-{orig_name}。テンプレートでエラーが発生した場合、フォールバック {post_id}_{orig_name} が使用されます。",
                "korean": "템플릿에서 자리 표시자를 사용할 수 있습니다:\n{post_title}, {post_id}, {orig_name}, {ext}, {creator_name}, {creator_id}, {file_index}, {total_files}\n예: {post_title}-{post_id}-{orig_name}. 오류가 발생하면 기본값 {post_id}_{orig_name} 가 사용됩니다.",
                "chinese-simplified": "可以在模板中使用占位符:\n{post_title}, {post_id}, {orig_name}, {ext}, {creator_name}, {creator_id}, {file_index}, {total_files}\n示例: {post_title}-{post_id}-{orig_name}。如果模板出错，将使用回退 {post_id}_{orig_name}。",
            },
            "filename_template_error": {
                "english": "Filename template failed to format, using fallback: {0}",
                "japanese": "ファイル名テンプレートのフォーマットに失敗したため、フォールバックを使用します: {0}",
                "korean": "파일 이름 템플릿 형식 지정에 실패하여 폴백을 사용합니다: {0}",
                "chinese-simplified": "文件名模板格式化失败，使用回退: {0}",
            },
            "folder_strategy": {
                "english": "Folder Structure",
                "japanese": "フォルダ構造",
                "korean": "폴더 구조",
                "chinese-simplified": "文件夹结构",
            },
            "per_post_folders": {
                "english": "Per-post folders (default)",
                "japanese": "投稿ごとのフォルダ（デフォルト）",
                "korean": "게시물별 폴더 (기본)",
                "chinese-simplified": "按帖子创建子文件夹（默认）",
            },
            "single_creator_folder": {
                "english": "All files in creator folder",
                "japanese": "すべてのファイルをクリエーターフォルダに保存",
                "korean": "모든 파일을 크리에이터 폴더에 저장",
                "chinese-simplified": "将所有文件保存在创作者文件夹中",
            },
            "subfolders_by_file_type": {
                "english": "Subfolders by file type",
                "japanese": "ファイルタイプ別にサブフォルダを作成",
                "korean": "파일 유형별 하위 폴더",
                "chinese-simplified": "按文件类型创建子文件夹",
            },
            "open_directory": {
                "english": "Open Directory",
                "japanese": "ディレクトリを開く",
                "korean": "디렉토리 열기",
                "chinese-simplified": "打开目录",
            },
            "download_failed_retrying": {
                "english": "Download failed for {0}, attempt {1}/{2}: {3}",
                "japanese": "{0}のダウンロードに失敗しました、試行{1}/{2}：{3}",
                "korean": "{0} 다운로드 실패, 시도 {1}/{2}: {3}",
                "chinese-simplified": "{0}下载失败，尝试 {1}/{2}: {3}",
            },
            "error_downloading_after_retries": {
                "english": "Failed to download {0} after {1} retries: {2}",
                "japanese": "{1}回の試行後に{0}のダウンロードに失敗しました：{2}",
                "korean": "{1}번의 시도 후 {0} 다운로드 실패: {2}",
                "chinese-simplified": "尝试 {1} 次后下载 {0} 失败: {2}",
            },
            "size_mismatch_error": {
                "english": "Downloaded size ({0} bytes) does not match expected size ({1} bytes) for {2}",
                "japanese": "ダウンロードサイズ（{0}バイト）が予期されるサイズ（{1}バイト）と一致しません：{2}",
                "korean": "다운로드된 크기({0}바이트)가 예상 크기({1}바이트)와 일치하지 않습니다: {2}",
                "chinese-simplified": "下载大小（{0}字节）与预期大小（{1}字节）不匹配：{2}",
            },
            "deleted_incomplete_file": {
                "english": "Deleted incomplete file: {0}",
                "japanese": "不完全なファイルを削除しました：{0}",
                "korean": "불완전한 파일 삭제됨: {0}",
                "chinese-simplified": "已删除不完整的文件：{0}",
            },
            "failed_to_delete_incomplete_file": {
                "english": "Failed to delete incomplete file {0}: {1}",
                "japanese": "不完全なファイル{0}の削除に失敗しました：{1}",
                "korean": "불완전한 파일 {0} 삭제 실패: {1}",
                "chinese-simplified": "删除不完整的文件 {0} 失败：{1}",
            },
            "retry_countdown": {
                "english": "Trying again in {0}...",
                "japanese": "{0}秒後に再試行します...",
                "korean": "{0}초 후 다시 시도...",
                "chinese-simplified": "{0}秒后重试...",
            },
            # Reset to defaults translation
            "reset_to_defaults": {
                "english": "Reset to Defaults",
                "japanese": "デフォルトにリセット",
                "korean": "기본값으로 재설정",
                "chinese-simplified": "重置为默认值",
            },
            "confirm_reset_message": {
                "english": "Are you sure you want to reset all settings to their default values?",
                "japanese": "すべての設定をデフォルト値にリセットしてもよろしいですか？",
                "korean": "모든 설정을 기본값으로 재설정하시겠습니까?",
                "chinese-simplified": "您确定要将所有设置重置为默认值吗？",
            },
            "settings_reset_message": {
                "english": "Settings have been reset to defaults. Click 'Apply Changes' to save them.",
                "japanese": "設定がデフォルトにリセットされました。'変更を適用'をクリックして保存してください。",
                "korean": "설정이 기본값으로 재설정되었습니다. '변경 적용'을 클릭하여 저장하세요.",
                "chinese-simplified": "设置已重置为默认值。单击“应用更改”以保存它们。",
            },
            # For post_downloader.py fallback validation
            "attempting_fallback_validation": {
                "english": "Attempting fallback validation for {0}",
                "japanese": "{0} のフォールバック検証を試みています",
                "korean": "{0}에 대한 대체 검증 시도 중",
                "chinese-simplified": "尝试备用验证：{0}",
            },
            "url_validated_fallback": {
                "english": "URL validated using fallback method: {0}",
                "japanese": "フォールバック方法を使用してURLが検証されました: {0}",
                "korean": "대체 방법을 사용하여 URL이 검증됨: {0}",
                "chinese-simplified": "使用备用方法验证的 URL：{0}",
            },
            "fallback_validation_failed": {
                "english": "Fallback validation failed with exception: {0}",
                "japanese": "フォールバック検証が例外で失敗しました: {0}",
                "korean": "대체 검증이 예외로 실패했습니다: {0}",
                "chinese-simplified": "备用验证失败：{0}",
            },
            # For creator_downloader.py fallback validation
            # Main window and common elements
            "app_title": {
                "english": "Kemono Downloader",
                "japanese": "ケモノダウンローダー",
                "korean": "케모노 다운로더",
                "chinese-simplified": "Kemono 下载器",
            },
            "developed_by": {
                "english": "Developed by VoxDroid",
                "japanese": "開発者: VoxDroid",
                "korean": "개발자: VoxDroid",
                "chinese-simplified": "开发者: VoxDroid",
            },
            "launch_button": {
                "english": "Launch Application",
                "japanese": "アプリケーションを起動",
                "korean": "애플리케이션 시작",
                "chinese-simplified": "启动应用程序",
            },
            "idle": {
                "english": "Idle",
                "japanese": "アイドル",
                "korean": "대기 중",
                "chinese-simplified": "空闲",
            },
            # Tab names
            "post_downloader_tab": {
                "english": "Post Downloader",
                "japanese": "投稿ダウンローダー",
                "korean": "게시물 다운로더",
                "chinese-simplified": "投稿下载器",
            },
            "creator_downloader_tab": {
                "english": "Creator Downloader",
                "japanese": "クリエイターダウンローダー",
                "korean": "크리에이터 다운로더",
                "chinese-simplified": "创作者下载器",
            },
            "settings_tab": {
                "english": "Settings",
                "japanese": "設定",
                "korean": "설정",
                "chinese-simplified": "设置",
            },
            "help_tab": {
                "english": "Help",
                "japanese": "ヘルプ",
                "korean": "도움말",
                "chinese-simplified": "帮助",
            },
            "extension_tab": {
                "english": "Browser Extension",
                "japanese": "ブラウザ拡張機能",
                "korean": "브라우저 확장",
                "chinese-simplified": "浏览器扩展",
            },
            # Common buttons and actions
            "add_to_queue": {
                "english": "Add to Queue",
                "japanese": "キューに追加",
                "korean": "대기열에 추가",
                "chinese-simplified": "添加到队列",
            },
            "download": {
                "english": "Download",
                "japanese": "ダウンロード",
                "korean": "다운로드",
                "chinese-simplified": "下载",
            },
            "cancel": {
                "english": "Cancel",
                "japanese": "キャンセル",
                "korean": "취소",
                "chinese-simplified": "取消",
            },
            "apply_changes": {
                "english": "Apply Changes",
                "japanese": "変更を適用",
                "korean": "변경 적용",
                "chinese-simplified": "应用更改",
            },
            "browse": {
                "english": "Browse",
                "japanese": "参照",
                "korean": "찾아보기",
                "chinese-simplified": "浏览",
            },
            # Post Downloader tab
            "enter_post_url": {
                "english": "Enter post URL (e.g., https://kemono.cr/patreon/user/12345678/post/123456789)",
                "japanese": "投稿URLを入力 (例: https://kemono.cr/patreon/user/12345678/post/123456789)",
                "korean": "게시물 URL 입력 (예: https://kemono.cr/patreon/user/12345678/post/123456789)",
                "chinese-simplified": "输入投稿 URL (例如: https://kemono.cr/patreon/user/12345678/post/123456789)",
            },
            "post_queue": {
                "english": "Post Queue",
                "japanese": "投稿キュー",
                "korean": "게시물 대기열",
                "chinese-simplified": "投稿队列",
            },
            "files_to_download": {
                "english": "Files to Download",
                "japanese": "ダウンロードするファイル",
                "korean": "다운로드할 파일",
                "chinese-simplified": "将要下载的文件",
            },
            "filter_by_type": {
                "english": "Filter by Type",
                "japanese": "タイプでフィルタリング",
                "korean": "유형별 필터링",
                "chinese-simplified": "按类型过滤",
            },
            "search_items": {
                "english": "Search items...",
                "japanese": "アイテムを検索...",
                "korean": "항목 검색...",
                "chinese-simplified": "搜索项目...",
            },
            "check_all": {
                "english": "Check ALL (Page)",
                "japanese": "すべてチェック (ページ)",
                "korean": "모두 선택 (페이지)",
                "chinese-simplified": "全选 (页面)",
            },
            "check_all_all": {
                "english": "Check ALL (All)",
                "japanese": "すべてチェック (すべて)",
                "korean": "모두 선택 (모두)",
                "chinese-simplified": "全选 (全部)",
            },
            "download_all_links": {
                "english": "Download All Links",
                "japanese": "すべてのリンクをダウンロード",
                "korean": "모든 링크 다운로드",
                "chinese-simplified": "下载所有链接",
            },
            "files_count": {
                "english": "Files: {0}",
                "japanese": "ファイル: {0}",
                "korean": "파일: {0}",
                "chinese-simplified": "文件: {0}",
            },
            "file_progress": {
                "english": "File Progress {0}%",
                "japanese": "ファイル進捗 {0}%",
                "korean": "파일 진행률 {0}%",
                "chinese-simplified": "文件进度 {0}%",
            },
            "overall_progress": {
                "english": "Overall Progress ({0}/{1} files, {2}/{3} posts)",
                "japanese": "全体の進捗 ({0}/{1} ファイル, {2}/{3} 投稿)",
                "korean": "전체 진행률 ({0}/{1} 파일, {2}/{3} 게시물)",
                "chinese-simplified": "整体进度 ({0}/{1} 文件, {2}/{3} 投稿)",
            },
            "thumbnail_overall_progress": {
                "english": "Thumbnails: {0}/{1}",
                "japanese": "サムネイル: {0}/{1}",
                "korean": "썸네일: {0}/{1}",
                "chinese-simplified": "缩略图: {0}/{1}",
            },
            # Creator Downloader tab
            "enter_creator_url": {
                "english": "Enter creator URL (e.g., https://kemono.cr/patreon/user/12345678)",
                "japanese": "クリエイターURLを入力 (例: https://kemono.cr/patreon/user/12345678)",
                "korean": "크리에이터 URL 입력 (예: https://kemono.cr/patreon/user/12345678)",
                "chinese-simplified": "输入创作者 URL (例如: https://kemono.cr/patreon/user/12345678)",
            },
            "creator_queue": {
                "english": "Creator Queue",
                "japanese": "クリエイターキュー",
                "korean": "크리에이터 대기열",
                "chinese-simplified": "创作者队列",
            },
            "download_options": {
                "english": "Download Options",
                "japanese": "ダウンロードオプション",
                "korean": "다운로드 옵션",
                "chinese-simplified": "下载选项",
            },
            "main_file": {
                "english": "Main File",
                "japanese": "メインファイル",
                "korean": "메인 파일",
                "chinese-simplified": "主要文件",
            },
            "attachments": {
                "english": "Attachments",
                "japanese": "添付ファイル",
                "korean": "첨부 파일",
                "chinese-simplified": "附件",
            },
            "content_images": {
                "english": "Content Images",
                "japanese": "コンテンツ画像",
                "korean": "콘텐츠 이미지",
                "chinese-simplified": "内容图片",
            },
            "file_extensions": {
                "english": "File Extensions",
                "japanese": "ファイル拡張子",
                "korean": "파일 확장자",
                "chinese-simplified": "文件扩展名",
            },
            "download_text": {
                "english": "Download Post Text",
                "japanese": "投稿テキストをダウンロード",
                "korean": "게시물 텍스트 다운로드",
                "chinese-simplified": "下载帖子文本",
            },
            "saved_post_description": {
                "english": "Saved description for post {0}",
                "japanese": "投稿 {0} の説明を保存しました",
                "korean": "게시물 {0}의 설명을 저장했습니다",
                "chinese-simplified": "已保存帖子 {0} 的描述",
            },
            "failed_save_post_description": {
                "english": "Failed to save description for post {0}: {1}",
                "japanese": "投稿 {0} の説明の保存に失敗しました：{1}",
                "korean": "게시물 {0}의 설명 저장에 실패했습니다: {1}",
                "chinese-simplified": "保存帖子 {0} 的描述失败：{1}",
            },
            "posts_to_download": {
                "english": "Posts to Download",
                "japanese": "ダウンロードする投稿",
                "korean": "다운로드할 게시물",
                "chinese-simplified": "将要下载的投稿",
            },
            "search_posts": {
                "english": "Search posts...",
                "japanese": "投稿を検索...",
                "korean": "게시물 검색...",
                "chinese-simplified": "搜索投稿...",
            },
            "posts_count": {
                "english": "Posts: {0}",
                "japanese": "投稿: {0}",
                "korean": "게시물: {0}",
                "chinese-simplified": "投稿: {0}",
            },
            "page_info": {
                "english": "Page {0} of {1}",
                "japanese": "ページ {0} / {1}",
                "korean": "페이지 {0} / {1}",
                "chinese-simplified": "第 {0} 页，共 {1} 页",
            },
            # Settings tab
            "folder_settings": {
                "english": "Folder Settings",
                "japanese": "フォルダ設定",
                "korean": "폴더 설정",
                "chinese-simplified": "文件夹设置",
            },
            "folder_name": {
                "english": "Folder Name:",
                "japanese": "フォルダ名:",
                "korean": "폴더 이름:",
                "chinese-simplified": "文件夹名称:",
            },
            "save_directory": {
                "english": "Save Directory:",
                "japanese": "保存ディレクトリ:",
                "korean": "저장 디렉토리:",
                "chinese-simplified": "保存目录:",
            },
            "download_settings": {
                "english": "Download Settings",
                "japanese": "ダウンロード設定",
                "korean": "다운로드 설정",
                "chinese-simplified": "下载设置",
            },
            "simultaneous_downloads": {
                "english": "Simultaneous Downloads:",
                "japanese": "同時ダウンロード数:",
                "korean": "동시 다운로드:",
                "chinese-simplified": "并行下载数:",
            },
            "pawchive_policy_info_title": {
                "english": "Pawchive Download Policy",
                "japanese": "Pawchive ダウンロードポリシー",
                "korean": "Pawchive 다운로드 정책",
                "chinese-simplified": "Pawchive 下载策略",
            },
            "pawchive_policy_info_text": {
                "english": (
                    "To respect Pawchive's file servers, downloads use an "
                    "identifiable KemonoDownloader user agent. Pawchive file "
                    "requests are started at most once per second and are limited "
                    "to five active downloads across both downloaders.\n\n"
                    "Your Simultaneous Downloads setting still applies. For Pawchive, "
                    "the effective limit is the lower of your setting and five. "
                    "Kemono.cr and Coomer.st downloads are not affected by this policy."
                ),
                "japanese": (
                    "Pawchiveのファイルサーバーに配慮し、ダウンロードでは識別可能な"
                    "KemonoDownloaderのユーザーエージェントを使用します。Pawchiveへの"
                    "ファイルリクエストは1秒に最大1回、同時ダウンロードは両方のダウンローダー"
                    "を合わせて最大5件です。\n\n"
                    "同時ダウンロード数の設定は引き続き適用されます。Pawchiveでは設定値と"
                    "5の小さい方が有効な上限になります。Kemono.crとCoomer.stには影響しません。"
                ),
                "korean": (
                    "Pawchive 파일 서버를 존중하기 위해 다운로드 시 식별 가능한 "
                    "KemonoDownloader 사용자 에이전트를 사용합니다. Pawchive 파일 "
                    "요청은 1초에 최대 한 번 시작되며 두 다운로더를 합쳐 동시에 최대 5개로 "
                    "제한됩니다.\n\n"
                    "동시 다운로드 설정은 계속 적용됩니다. Pawchive에서는 설정값과 5 중 더 "
                    "작은 값이 실제 제한입니다. Kemono.cr 및 Coomer.st에는 이 정책이 적용되지 않습니다."
                ),
                "chinese-simplified": (
                    "为尊重 Pawchive 文件服务器，下载时会使用可识别的 "
                    "KemonoDownloader 用户代理。Pawchive 文件请求最多每秒启动一次，两个下载器"
                    "合计最多同时进行 5 个下载。\n\n"
                    "并行下载数设置仍然有效。对于 Pawchive，实际限制是设置值和 5 中较小的值。"
                    "Kemono.cr 和 Coomer.st 不受此策略影响。"
                ),
            },
            "retry_settings": {
                "english": "Retry Settings",
                "japanese": "リトライ設定",
                "korean": "재시도 설정",
                "chinese-simplified": "重试设置",
            },
            "creator_posts_max_attempts": {
                "english": "Creator Posts Max Attempts:",
                "japanese": "クリエイター投稿最大試行回数:",
                "korean": "크리에이터 게시물 최대 시도 횟수:",
                "chinese-simplified": "创作者帖子最大尝试次数:",
            },
            "post_data_max_retries": {
                "english": "Post Data Max Retries:",
                "japanese": "投稿データ最大リトライ回数:",
                "korean": "게시물 데이터 최대 재시도 횟수:",
                "chinese-simplified": "帖子数据最大重试次数:",
            },
            "file_download_max_retries": {
                "english": "File Download Max Retries:",
                "japanese": "ファイルダウンロード最大リトライ回数:",
                "korean": "파일 다운로드 최대 재시도 횟수:",
                "chinese-simplified": "文件下载最大重试次数:",
            },
            "api_request_max_retries": {
                "english": "API Request Max Retries:",
                "japanese": "APIリクエスト最大リトライ回数:",
                "korean": "API 요청 최대 재시도 횟수:",
                "chinese-simplified": "API请求最大重试次数:",
            },
            "update_settings": {
                "english": "Update Settings",
                "japanese": "更新設定",
                "korean": "업데이트 설정",
                "chinese-simplified": "更新设置",
            },
            "auto_check_updates": {
                "english": "Auto Check for Updates:",
                "japanese": "自動更新チェック:",
                "korean": "자동 업데이트 확인:",
                "chinese-simplified": "自动检查更新:",
            },
            "language_settings": {
                "english": "Language Settings",
                "japanese": "言語設定",
                "korean": "언어 설정",
                "chinese-simplified": "语言设置",
            },
            "language": {
                "english": "Language:",
                "japanese": "言語:",
                "korean": "언어:",
                "chinese-simplified": "语言:",
            },
            "english": {
                "english": "English",
                "japanese": "英語",
                "korean": "영어",
                "chinese-simplified": "英语",
            },
            "japanese": {
                "english": "Japanese",
                "japanese": "日本語",
                "korean": "일본어",
                "chinese-simplified": "日语",
            },
            "korean": {
                "english": "Korean",
                "japanese": "韓国語",
                "korean": "한국어",
                "chinese-simplified": "韩语",
            },
            "chinese-simplified": {
                "english": "Chinese (Simplified)",
                "japanese": "中国語 (簡体字)",
                "korean": "중국어 (간체)",
                "chinese-simplified": "中文 (简体)",
            },
            # Font settings
            "font_settings": {
                "english": "Font Settings",
                "japanese": "フォント設定",
                "korean": "글꼴 설정",
                "chinese-simplified": "字体设置",
            },
            "font": {
                "english": "Font:",
                "japanese": "フォント:",
                "korean": "글꼴:",
                "chinese-simplified": "字体:",
            },
            "full_logs": {
                "english": "Full Logs",
                "japanese": "完全なログ",
                "korean": "전체 로그",
                "chinese-simplified": "完整日志",
            },
            "clear_logs": {
                "english": "Clear Logs",
                "japanese": "ログをクリア",
                "korean": "로그 지우기",
                "chinese-simplified": "清除日志",
            },
            "download_logs": {
                "english": "Download Logs",
                "japanese": "ログをダウンロード",
                "korean": "로그 다운로드",
                "chinese-simplified": "下载日志",
            },
            # Confirmation dialogs
            "confirm_settings_change": {
                "english": "Confirm Settings Change",
                "japanese": "設定変更の確認",
                "korean": "설정 변경 확인",
                "chinese-simplified": "确认设置更改",
            },
            "confirm_settings_message": {
                "english": "Are you sure you want to apply these settings?\n\nFolder Name: {0}\nSave Directory: {1}\nSimultaneous Downloads: {2}\nAuto Check Updates: {3}\nLanguage: {4}\nUse Proxy: {5}\nProxy Type: {6}\nFilename Template: {7}\nFolder Strategy: {8}\nFont: {9}",
                "japanese": "これらの設定を適用してもよろしいですか？\n\nフォルダ名: {0}\n保存ディレクトリ: {1}\n同時ダウンロード数: {2}\n自動更新チェック: {3}\n言語: {4}\nプロキシを使用: {5}\nプロキシタイプ: {6}\nファイル名テンプレート: {7}\nフォルダ戦略: {8}\nフォント: {9}",
                "korean": "이 설정을 적용하시겠습니까?\n\n폴더 이름: {0}\n저장 디렉토리: {1}\n동시 다운로드: {2}\n자동 업데이트 확인: {3}\n언어: {4}\n프록시 사용: {5}\n프록시 유형: {6}\n파일 이름 템플릿: {7}\n폴더 전략: {8}\n글꼴: {9}",
                "chinese-simplified": "您确定要应用这些设置吗？\n\n文件夹名称: {0}\n保存目录: {1}\n并行下载数: {2}\n自动检查更新: {3}\n语言: {4}\n使用代理: {5}\n代理类型: {6}\n文件名模板: {7}\n文件夹策略: {8}\n字体: {9}",
            },
            "enabled": {
                "english": "Enabled",
                "japanese": "有効",
                "korean": "활성화",
                "chinese-simplified": "启用",
            },
            "disabled": {
                "english": "Disabled",
                "japanese": "無効",
                "korean": "비활성화",
                "chinese-simplified": "禁用",
            },
            "settings_applied": {
                "english": "Settings Applied",
                "japanese": "設定が適用されました",
                "korean": "설정 적용됨",
                "chinese-simplified": "设置已应用",
            },
            "settings_applied_message": {
                "english": "Settings have been successfully applied!\n\nFolder Name: {0}\nSave Directory: {1}\nSimultaneous Downloads: {2}\nAuto Check Updates: {3}\nLanguage: {4}\nUse Proxy: {5}\nProxy Type: {6}\nFilename Template: {7}\nFolder Strategy: {8}\nFont: {9}",
                "japanese": "設定が正常に適用されました！\n\nフォルダ名: {0}\n保存ディレクトリ: {1}\n同時ダウンロード数: {2}\n自動更新チェック: {3}\n言語: {4}\nプロキシを使用: {5}\nプロキシタイプ: {6}\nファイル名テンプレート: {7}\nフォルダ戦略: {8}\nフォント: {9}",
                "korean": "설정이 성공적으로 적용되었습니다!\n\n폴더 이름: {0}\n저장 디렉토리: {1}\n동시 다운로드: {2}\n자동 업데이트 확인: {3}\n언어: {4}\n프록시 사용: {5}\n프록시 유형: {6}\n파일 이름 템플릿: {7}\n폴더 전략: {8}\n글꼴: {9}",
                "chinese-simplified": "设置已成功应用！\n\n文件夹名称: {0}\n保存目录: {1}\n并行下载数: {2}\n自动检查更新: {3}\n语言: {4}\n使用代理: {5}\n代理类型: {6}\n文件名模板: {7}\n文件夹策略: {8}\n字体: {9}",
            },
            "proxy_settings": {
                "english": "Proxy Settings",
                "japanese": "プロキシ設定",
                "korean": "프록시 설정",
                "chinese-simplified": "代理设置",
            },
            "use_proxy": {
                "english": "Use Proxy",
                "japanese": "プロキシを使用",
                "korean": "프록시 사용",
                "chinese-simplified": "使用代理",
            },
            "proxy_type": {
                "english": "Proxy Type:",
                "japanese": "プロキシタイプ:",
                "korean": "프록시 유형:",
                "chinese-simplified": "代理类型:",
            },
            "custom_proxy_url": {
                "english": "Custom Proxy URL:",
                "japanese": "カスタムプロキシURL:",
                "korean": "사용자 정의 프록시 URL:",
                "chinese-simplified": "自定义代理URL:",
            },
            "test_proxy": {
                "english": "Test Proxy",
                "japanese": "プロキシをテスト",
                "korean": "프록시 테스트",
                "chinese-simplified": "测试代理",
            },
            "tor_path": {
                "english": "Tor Path:",
                "japanese": "Torパス:",
                "korean": "Tor 경로:",
                "chinese-simplified": "Tor路径:",
            },
            "download_tor": {
                "english": "Download Tor",
                "japanese": "Torをダウンロード",
                "korean": "Tor 다운로드",
                "chinese-simplified": "下载Tor",
            },
            "test_tor": {
                "english": "Test Tor",
                "japanese": "Torをテスト",
                "korean": "Tor 테스트",
                "chinese-simplified": "测试Tor",
            },
            "custom_proxy_url_empty": {
                "english": "Custom proxy URL cannot be empty.",
                "japanese": "カスタムプロキシURLは空にできません。",
                "korean": "사용자 정의 프록시 URL은 비워둘 수 없습니다.",
                "chinese-simplified": "自定义代理URL不能为空。",
            },
            "proxy_test_successful": {
                "english": "Proxy test successful!",
                "japanese": "プロキシテスト成功！",
                "korean": "프록시 테스트 성공!",
                "chinese-simplified": "代理测试成功！",
            },
            "proxy_test_failed": {
                "english": "Proxy test failed: {0}",
                "japanese": "プロキシテスト失敗: {0}",
                "korean": "프록시 테스트 실패: {0}",
                "chinese-simplified": "代理测试失败: {0}",
            },
            "downloading_tor": {
                "english": "Downloading Tor...",
                "japanese": "Torをダウンロード中...",
                "korean": "Tor 다운로드 중...",
                "chinese-simplified": "正在下载Tor...",
            },
            "downloading": {
                "english": "Downloading...",
                "japanese": "ダウンロード中...",
                "korean": "다운로드 중...",
                "chinese-simplified": "下载中...",
            },
            "tor_download_successful": {
                "english": "Tor downloaded successfully!",
                "japanese": "Torのダウンロードに成功しました！",
                "korean": "Tor 다운로드 성공!",
                "chinese-simplified": "Tor下载成功！",
            },
            "tor_download_failed": {
                "english": "Tor download failed: {0}",
                "japanese": "Torダウンロード失敗: {0}",
                "korean": "Tor 다운로드 실패: {0}",
                "chinese-simplified": "Tor下载失败: {0}",
            },
            "tor_exe_not_found": {
                "english": "tor.exe not found in downloaded files.",
                "japanese": "ダウンロードしたファイルにtor.exeが見つかりません。",
                "korean": "다운로드한 파일에서 tor.exe를 찾을 수 없습니다.",
                "chinese-simplified": "在下载的文件中找不到tor.exe。",
            },
            "tor_not_configured": {
                "english": "Tor is not configured or tor.exe not found.",
                "japanese": "Torが設定されていないか、tor.exeが見つかりません。",
                "korean": "Tor가 구성되지 않았거나 tor.exe를 찾을 수 없습니다.",
                "chinese-simplified": "Tor未配置或找不到tor.exe。",
            },
            "tor_test_successful": {
                "english": "Tor test successful!",
                "japanese": "Torテスト成功！",
                "korean": "Tor 테스트 성공!",
                "chinese-simplified": "Tor测试成功！",
            },
            "tor_test_failed": {
                "english": "Tor test failed.",
                "japanese": "Torテスト失敗。",
                "korean": "Tor 테스트 실패.",
                "chinese-simplified": "Tor测试失败。",
            },
            "tor_unsupported_platform": {
                "english": "Tor download is not supported on this platform.",
                "japanese": "このプラットフォームではTorのダウンロードはサポートされていません。",
                "korean": "이 플랫폼에서는 Tor 다운로드를 지원하지 않습니다.",
                "chinese-simplified": "此平台不支持Tor下载。",
            },
            "tor_auto_detected": {
                "english": "Tor automatically detected at: {0}",
                "japanese": "Torが自動検出されました: {0}",
                "korean": "Tor가 자동으로 감지되었습니다: {0}",
                "chinese-simplified": "Tor已自动检测到: {0}",
            },
            "start_tor": {
                "english": "Start Tor",
                "japanese": "Torを開始",
                "korean": "Tor 시작",
                "chinese-simplified": "启动Tor",
            },
            "stop_tor": {
                "english": "Stop Tor",
                "japanese": "Torを停止",
                "korean": "Tor 중지",
                "chinese-simplified": "停止Tor",
            },
            "tor_starting": {
                "english": "Starting Tor...",
                "japanese": "Torを開始中...",
                "korean": "Tor 시작 중...",
                "chinese-simplified": "正在启动Tor...",
            },
            "tor_running": {
                "english": "Tor is now running and ready to use.",
                "japanese": "Torが実行中です。使用可能です。",
                "korean": "Tor가 실행 중입니다. 사용할 수 있습니다.",
                "chinese-simplified": "Tor正在运行，可以使用。",
            },
            "tor_stopped": {
                "english": "Tor has been stopped.",
                "japanese": "Torが停止されました。",
                "korean": "Tor가 중지되었습니다.",
                "chinese-simplified": "Tor已停止。",
            },
            "tor_already_running": {
                "english": "Tor is already running.",
                "japanese": "Torはすでに実行中です。",
                "korean": "Tor가 이미 실행 중입니다.",
                "chinese-simplified": "Tor已经在运行。",
            },
            "tor_not_running": {
                "english": "Tor is not currently running.",
                "japanese": "Torは現在実行されていません。",
                "korean": "Tor가 현재 실행되고 있지 않습니다.",
                "chinese-simplified": "Tor当前未运行。",
            },
            "tor_proxy_working": {
                "english": "Tor proxy is working correctly!",
                "japanese": "Torプロキシが正常に動作しています！",
                "korean": "Tor 프록시가 올바르게 작동하고 있습니다!",
                "chinese-simplified": "Tor代理正常工作！",
            },
            "tor_executable_ok_but_proxy_not_running": {
                "english": "Tor executable is valid, but proxy service is not running. Please start Tor first.",
                "japanese": "Tor実行ファイルは有効ですが、プロキシサービスが実行されていません。まずTorを開始してください。",
                "korean": "Tor 실행 파일은 유효하지만 프록시 서비스가 실행되고 있지 않습니다. 먼저 Tor를 시작하십시오.",
                "chinese-simplified": "Tor可执行文件有效，但代理服务未运行。请先启动Tor。",
            },
            "tor_output": {
                "english": "Tor Output:",
                "japanese": "Tor出力:",
                "korean": "Tor 출력:",
                "chinese-simplified": "Tor输出:",
            },
            "confirm_removal": {
                "english": "Confirm Removal",
                "japanese": "削除の確認",
                "korean": "제거 확인",
                "chinese-simplified": "确认删除",
            },
            "confirm_removal_message": {
                "english": "Are you sure you want to remove {0} from the queue?",
                "japanese": "キューから {0} を削除してもよろしいですか？",
                "korean": "대기열에서 {0}을(를) 제거하시겠습니까?",
                "chinese-simplified": "您确定要从队列中删除 {0} 吗？",
            },
            "remove_thread": {
                "english": "Removed thread {0} from active threads",
                "japanese": "アクティブなスレッドからスレッド {0} を削除しました",
                "korean": "활성 스레드에서 스레드 {0}을 제거했습니다",
                "chinese-simplified": "从活跃线程中移除线程 {0}",
            },
            "transferred_from": {
                "english": "Transferred {0} from {1}",
                "japanese": "{1} から {0} を転送しました",
                "korean": "{1}에서 {0}을(를) 전송했습니다",
                "chinese-simplified": "从 {1} 转移了 {0}",
            },
            "all_files_attempted_for_creator": {
                "english": "All files attempted for current creator. Finalizing.",
                "japanese": "現在のクリエイターのすべてのファイルの試行が完了しました。最終処理中。",
                "korean": "현재 크리에이터의 모든 파일 시도가 완료되었습니다. 마무리 중입니다.",
                "chinese-simplified": "当前创建者的所有文件尝试已完成。正在完成。",
            },
            # Error messages
            "invalid_input": {
                "english": "Invalid Input",
                "japanese": "無効な入力",
                "korean": "잘못된 입력",
                "chinese-simplified": "无效输入",
            },
            "folder_name_empty": {
                "english": "Folder name cannot be empty.",
                "japanese": "フォルダ名は空にできません。",
                "korean": "폴더 이름은 비워둘 수 없습니다.",
                "chinese-simplified": "文件夹名称不能为空。",
            },
            "update_check_failed": {
                "english": "Update Check Failed",
                "japanese": "更新チェックに失敗しました",
                "korean": "업데이트 확인 실패",
                "chinese-simplified": "检查更新失败",
            },
            "unable_check_updates": {
                "english": "Unable to check for updates.",
                "japanese": "更新を確認できません。",
                "korean": "업데이트를 확인할 수 없습니다.",
                "chinese-simplified": "无法检查更新。",
            },
            "image_load_error": {
                "english": "Image Load Error",
                "japanese": "画像読み込みエラー",
                "korean": "이미지 로드 오류",
                "chinese-simplified": "图片加载错误",
            },
            "media_load_error": {
                "english": "Media Load Error",
                "japanese": "メディア読み込みエラー",
                "korean": "미디어 로드 오류",
                "chinese-simplified": "媒体加载错误",
            },
            # Update notification
            "update_available": {
                "english": "Update Available",
                "japanese": "更新があります",
                "korean": "업데이트 가능",
                "chinese-simplified": "更新可用",
            },
            "update_available_message": {
                "english": "A new version ({0}) is available!",
                "japanese": "新しいバージョン ({0}) が利用可能です！",
                "korean": "새 버전({0})이 사용 가능합니다!",
                "chinese-simplified": "新版本 ({0}) 可用！",
            },
            "current_version": {
                "english": "Current version: {0}",
                "japanese": "現在のバージョン: {0}",
                "korean": "현재 버전: {0}",
                "chinese-simplified": "当前版本: {0}",
            },
            "click_release_page": {
                "english": "Click here to visit the release page",
                "japanese": "リリースページを訪問するにはここをクリック",
                "korean": "릴리스 페이지를 방문하려면 여기를 클릭하세요",
                "chinese-simplified": "点击此处访问发布页面",
            },
            # Background tasks
            "detecting_post": {
                "english": "Detecting post from link...",
                "japanese": "リンクから投稿を検出中...",
                "korean": "링크에서 게시물 감지 중...",
                "chinese-simplified": "从链接检测投稿...",
            },
            "detecting_posts": {
                "english": "Detecting posts from link...",
                "japanese": "リンクから投稿を検出中...",
                "korean": "링크에서 게시물 감지 중...",
                "chinese-simplified": "从链接检测投稿...",
            },
            "validating_url": {
                "english": "Validating URL...",
                "japanese": "URLを検証中...",
                "korean": "URL 검증 중...",
                "chinese-simplified": "验证 URL...",
            },
            "populating_posts": {
                "english": "Populating posts...",
                "japanese": "投稿を読み込み中...",
                "korean": "게시물 채우는 중...",
                "chinese-simplified": "添加投稿信息...",
            },
            "filtering_posts": {
                "english": "Filtering posts...",
                "japanese": "投稿をフィルタリング中...",
                "korean": "게시물 필터링 중...",
                "chinese-simplified": "过滤投稿...",
            },
            "preparing_files": {
                "english": "Preparing files to download...",
                "japanese": "ダウンロードするファイルを準備中...",
                "korean": "다운로드할 파일 준비 중...",
                "chinese-simplified": "准备下载文件...",
            },
            "updating_checkboxes": {
                "english": "Updating checkboxes...",
                "japanese": "チェックボックスを更新中...",
                "korean": "체크박스 업데이트 중...",
                "chinese-simplified": "更新复选框...",
            },
            "toggling_checkbox": {
                "english": "Toggling checkbox...",
                "japanese": "チェックボックスを切り替え中...",
                "korean": "체크박스 토글 중...",
                "chinese-simplified": "切换复选框...",
            },
            "loading_image": {
                "english": "Loading Image... ({0}%)",
                "japanese": "画像を読み込み中... ({0}%)",
                "korean": "이미지 로드 중... ({0}%)",
                "chinese-simplified": "加载图片... ({0}%)",
            },
            "loading_image_simple": {
                "english": "Loading Image...",
                "japanese": "画像を読み込み中...",
                "korean": "이미지 로드 중...",
                "chinese-simplified": "加载图片...",
            },
            "error_loading_image": {
                "english": "Error loading image",
                "japanese": "画像の読み込みエラー",
                "korean": "이미지 로드 오류",
                "chinese-simplified": "加载图片时出错",
            },
            # Log messages
            "log_info": {
                "english": "[INFO] {0}",
                "japanese": "[情報] {0}",
                "korean": "[정보] {0}",
                "chinese-simplified": "[消息] {0}",
            },
            "log_warning": {
                "english": "[WARNING] {0}",
                "japanese": "[警告] {0}",
                "korean": "[경고] {0}",
                "chinese-simplified": "[警告] {0}",
            },
            "log_error": {
                "english": "[ERROR] {0}",
                "japanese": "[エラー] {0}",
                "korean": "[오류] {0}",
                "chinese-simplified": "[错误] {0}",
            },
            "log_debug": {
                "english": "[DEBUG] {0}",
                "japanese": "[デバッグ] {0}",
                "korean": "[디버그] {0}",
                "chinese-simplified": "[调试] {0}",
            },
            # Common log messages
            "no_url_entered": {
                "english": "No URL entered.",
                "japanese": "URLが入力されていません。",
                "korean": "URL이 입력되지 않았습니다.",
                "chinese-simplified": "未输入 URL。",
            },
            "added_post_url": {
                "english": "Added post URL to queue: {0}",
                "japanese": "投稿URLをキューに追加しました: {0}",
                "korean": "게시물 URL을 대기열에 추가했습니다: {0}",
                "chinese-simplified": "已将投稿 URL 添加到队列: {0}",
            },
            "added_creator_url": {
                "english": "Added creator URL to queue: {0}",
                "japanese": "クリエイターURLをキューに追加しました: {0}",
                "korean": "크리에이터 URL을 대기열에 추가했습니다: {0}",
                "chinese-simplified": "已将创作者 URL 添加到队列: {0}",
            },
            "invalid_post_url": {
                "english": "Invalid post URL or failed to fetch: {0}",
                "japanese": "無効な投稿URLまたは取得に失敗しました: {0}",
                "korean": "잘못된 게시물 URL 또는 가져오기 실패: {0}",
                "chinese-simplified": "无效的投稿 URL 或获取失败: {0}",
            },
            "invalid_creator_url": {
                "english": "Invalid creator URL or failed to fetch: {0}",
                "japanese": "無効なクリエイターURLまたは取得に失敗しました: {0}",
                "korean": "잘못된 크리에이터 URL 또는 가져오기 실패: {0}",
                "chinese-simplified": "无效的创作者 URL 或获取失败: {0}",
            },
            "viewing_post": {
                "english": "Viewing post: {0}",
                "japanese": "投稿を表示中: {0}",
                "korean": "게시물 보는 중: {0}",
                "chinese-simplified": "查看投稿: {0}",
            },
            "viewing_creator": {
                "english": "Viewing creator: {0}",
                "japanese": "クリエイターを表示中: {0}",
                "korean": "크리에이터 보는 중: {0}",
                "chinese-simplified": "查看创作者: {0}",
            },
            "link_removed": {
                "english": "Link ({0}) is removed from the queue.",
                "japanese": "リンク ({0}) がキューから削除されました。",
                "korean": "링크 ({0})가 대기열에서 제거되었습니다.",
                "chinese-simplified": "链接 ({0}) 已从队列中删除。",
            },
            "url_not_found": {
                "english": "URL ({0}) not found in queue.",
                "japanese": "URL ({0}) がキューに見つかりません。",
                "korean": "URL ({0})이(가) 대기열에 없습니다.",
                "chinese-simplified": "队列中未找到 URL ({0})。",
            },
            "no_posts_queue": {
                "english": "No posts in queue to download.",
                "japanese": "ダウンロードするキューに投稿がありません。",
                "korean": "다운로드할 게시물이 대기열에 없습니다.",
                "chinese-simplified": "下载队列中没有投稿。",
            },
            "no_creators_queue": {
                "english": "No creators in queue to download.",
                "japanese": "ダウンロードするキューにクリエイターがありません。",
                "korean": "다운로드할 크리에이터가 대기열에 없습니다.",
                "chinese-simplified": "下载队列中没有创作者。",
            },
            "no_files_selected": {
                "english": "No files selected for download.",
                "japanese": "ダウンロードするファイルが選択されていません。",
                "korean": "다운로드할 파일이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的文件。",
            },
            "no_posts_selected": {
                "english": "No posts selected for download.",
                "japanese": "ダウンロードする投稿が選択されていません。",
                "korean": "다운로드할 게시물이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的投稿。",
            },
            "preparing_files_post": {
                "english": "Preparing files for currently viewed post: {0}",
                "japanese": "現在表示中の投稿のファイルを準備中: {0}",
                "korean": "현재 보고 있는 게시물의 파일 준비 중: {0}",
                "chinese-simplified": "正在准备当前查看的投稿的文件: {0}",
            },
            "preparing_files_creator": {
                "english": "Preparing files for currently viewed creator: {0}",
                "japanese": "現在表示中のクリエイターのファイルを準備中: {0}",
                "korean": "현재 보고 있는 크리에이터의 파일 준비 중: {0}",
                "chinese-simplified": "正在准备当前查看的创作者的文件: {0}",
            },
            "preparing_files_all_posts": {
                "english": "Preparing files for all posts in queue",
                "japanese": "キュー内のすべての投稿のファイルを準備中",
                "korean": "대기열의 모든 게시물에 대한 파일 준비 중",
                "chinese-simplified": "正在准备队列中所有投稿的文件",
            },
            "download_all_disabled": {
                "english": "Download All Links disabled. Reverted to current post.",
                "japanese": "すべてのリンクをダウンロードが無効になりました。現在の投稿に戻りました。",
                "korean": "모든 링크 다운로드 비활성화됨. 현재 게시물로 되돌아갔습니다.",
                "chinese-simplified": "下载所有链接已禁用。退回到当前投稿。",
            },
            "download_process_ended": {
                "english": "Download process ended",
                "japanese": "ダウンロードプロセスが終了しました",
                "korean": "다운로드 프로세스 종료",
                "chinese-simplified": "下载任务结束",
            },
            "download_process_completed": {
                "english": "Download process completed",
                "japanese": "ダウンロードプロセスが完了しました",
                "korean": "다운로드 프로세스 완료",
                "chinese-simplified": "下载任务完成",
            },
            "downloads_complete": {
                "english": "Downloads Complete",
                "japanese": "ダウンロード完了",
                "korean": "다운로드 완료",
                "chinese-simplified": "下载完毕",
            },
            "downloads_terminated": {
                "english": "Downloads Terminated",
                "japanese": "ダウンロード中断",
                "korean": "다운로드 중단됨",
                "chinese-simplified": "下载终止",
            },
            "cancelling_downloads": {
                "english": "Cancelling all downloads...",
                "japanese": "すべてのダウンロードをキャンセル中...",
                "korean": "모든 다운로드 취소 중...",
                "chinese-simplified": "正在取消所有下载...",
            },
            "cancelling_post_detection": {
                "english": "Cancelling post detection...",
                "japanese": "投稿検出をキャンセル中...",
                "korean": "게시물 감지 취소 중...",
                "chinese-simplified": "正在取消投稿检测...",
            },
            "all_downloads_cancelled": {
                "english": "All downloads cancelled by user",
                "japanese": "すべてのダウンロードがユーザーによってキャンセルされました",
                "korean": "모든 다운로드가 사용자에 의해 취소됨",
                "chinese-simplified": "所有下载已被用户取消",
            },
            "preview_not_supported": {
                "english": "Preview not supported for file type: {0} ({1})",
                "japanese": "ファイルタイプのプレビューはサポートされていません: {0} ({1})",
                "korean": "파일 유형에 대한 미리보기가 지원되지 않습니다: {0} ({1})",
                "chinese-simplified": "不支持预览的文件类型: {0} ({1})",
            },
            "no_item_selected": {
                "english": "No item selected for preview.",
                "japanese": "プレビューするアイテムが選択されていません。",
                "korean": "미리보기할 항목이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要预览的项目。",
            },
            "file_already_downloaded": {
                "english": "File {0} already downloaded at {1}, skipping.",
                "japanese": "ファイル {0} はすでに {1} にダウンロードされています。スキップします。",
                "korean": "파일 {0}이(가) 이미 {1}에 다운로드되었습니다. 건너뜁니다.",
                "chinese-simplified": "文件 {0} 已在 {1} 下载，跳过。",
            },
            "starting_download": {
                "english": "Starting download of file {0}/{1}: {2} to {3}",
                "japanese": "ファイル {0}/{1} のダウンロードを開始: {2} を {3} に",
                "korean": "파일 {0}/{1} 다운로드 시작: {2}을(를) {3}에",
                "chinese-simplified": "开始下载文件 {0}/{1}: {2} 到 {3}",
            },
            "successfully_downloaded": {
                "english": "Successfully downloaded: {0}",
                "japanese": "ダウンロード成功: {0}",
                "korean": "다운로드 성공: {0}",
                "chinese-simplified": "下载成功: {0}",
            },
            "download_interrupted": {
                "english": "Download interrupted for {0}",
                "japanese": "{0} のダウンロードが中断されました",
                "korean": "{0}에 대한 다운로드가 중단됨",
                "chinese-simplified": "{0} 的下载已中断",
            },
            "post_fully_downloaded": {
                "english": "Post {0} fully downloaded.",
                "japanese": "投稿 {0} が完全にダウンロードされました。",
                "korean": "게시물 {0}이(가) 완전히 다운로드되었습니다.",
                "chinese-simplified": "投稿 {0} 已完全下载。",
            },
            "all_files_downloaded": {
                "english": "All files for post {0} have been downloaded",
                "japanese": "投稿 {0} のすべてのファイルがダウンロードされました",
                "korean": "게시물 {0}의 모든 파일이 다운로드되었습니다",
                "chinese-simplified": "所有文件已下载完毕: {0}",
            },
            "language_changed": {
                "english": "Language changed to English",
                "japanese": "言語が日本語に変更されました",
                "korean": "언어가 한국어로 변경되었습니다",
                "chinese-simplified": "语言已更改为中文 (简体)",
            },
            # Media preview
            "media_preview": {
                "english": "Media Preview",
                "japanese": "メディアプレビュー",
                "korean": "미디어 미리보기",
                "chinese-simplified": "媒体预览",
            },
            "fit": {
                "english": "Fit",
                "japanese": "フィット",
                "korean": "맞춤",
                "chinese-simplified": "适合窗口",
            },
            "stretch": {
                "english": "Stretch",
                "japanese": "引き伸ばし",
                "korean": "늘이기",
                "chinese-simplified": "拉伸",
            },
            "original": {
                "english": "Original",
                "japanese": "オリジナル",
                "korean": "원본",
                "chinese-simplified": "原始大小",
            },
            "full_screen": {
                "english": "Full Screen (Modal)",
                "japanese": "全画面 (モーダル)",
                "korean": "전체 화면 (모달)",
                "chinese-simplified": "全屏 (模态)",
            },
            "audio_playback": {
                "english": "Audio Playback",
                "japanese": "オーディオ再生",
                "korean": "오디오 재생",
                "chinese-simplified": "音频播放",
            },
            "error_loading_media": {
                "english": "Error loading media",
                "japanese": "メディアの読み込みエラー",
                "korean": "미디어 로드 오류",
                "chinese-simplified": "加载媒体时出错",
            },
            # Error messages for media
            "invalid_url_format": {
                "english": "Invalid URL format. Expected: https://kemono.cr/[service]/user/[user_id]/post/[post_id]",
                "japanese": "無効なURL形式。期待される形式: https://kemono.cr/[service]/user/[user_id]/post/[post_id]",
                "korean": "잘못된 URL 형식. 예상 형식: https://kemono.cr/[service]/user/[user_id]/post/[post_id]",
                "chinese-simplified": "无效的 URL 格式。预期格式: https://kemono.cr/[service]/user/[user_id]/post/[post_id]",
            },
            "invalid_url_format_link": {
                "english": "Invalid URL format: {0}",
                "japanese": "無効なURL形式：{0}",
                "korean": "잘못된 URL 형식: {0}",
                "chinese-simplified": "无效的URL格式：{0}",
            },
            "failed_to_fetch_post": {
                "english": "Failed to fetch post - Status code: {0}",
                "japanese": "投稿の取得に失敗しました - ステータスコード: {0}",
                "korean": "게시물 가져오기 실패 - 상태 코드: {0}",
                "chinese-simplified": "获取投稿失败 - 状态码: {0}",
            },
            "failed_to_fetch_post_error": {
                "english": "Failed to fetch post: {0}",
                "japanese": "投稿の取得に失敗しました: {0}",
                "korean": "게시물 가져오기 실패: {0}",
                "chinese-simplified": "获取投稿失败: {0}",
            },
            "no_valid_post_data": {
                "english": "No valid post data returned",
                "japanese": "有効な投稿データが返されませんでした",
                "korean": "유효한 게시물 데이터가 반환되지 않았습니다",
                "chinese-simplified": "未返回有效的投稿数据",
            },
            "invalid_image_data": {
                "english": "Invalid or corrupted image data",
                "japanese": "無効または破損した画像データ",
                "korean": "잘못되거나 손상된 이미지 데이터",
                "chinese-simplified": "无效或损坏的图像数据",
            },
            "failed_to_download": {
                "english": "Failed to download file from",
                "japanese": "ファイルのダウンロードに失敗しました",
                "korean": "파일 다운로드 실패",
                "chinese-simplified": "下载文件失败",
            },
            "unexpected_error": {
                "english": "Unexpected error while processing file from",
                "japanese": "ファイル処理中に予期しないエラーが発生しました",
                "korean": "파일 처리 중 예기치 않은 오류 발생",
                "chinese-simplified": "处理文件时发生意外错误",
            },
            "failed_to_load_gif": {
                "english": "Failed to load GIF from {0}: Invalid or corrupted GIF data",
                "japanese": "{0} からGIFを読み込めませんでした: 無効または破損したGIFデータ",
                "korean": "{0}에서 GIF 로드 실패: 잘못되거나 손상된 GIF 데이터",
                "chinese-simplified": "无法从 {0} 加载 GIF: 无效或损坏的 GIF 数据",
            },
            "no_internet_connection": {
                "english": "No internet connection. Update check failed.",
                "japanese": "インターネット接続がありません。更新チェックに失敗しました。",
                "korean": "인터넷 연결이 없습니다. 업데이트 확인 실패.",
                "chinese-simplified": "没有互联网连接。检查更新失败。",
            },
            "failed_to_check_updates": {
                "english": "Failed to check for updates",
                "japanese": "更新の確認に失敗しました",
                "korean": "업데이트 확인 실패",
                "chinese-simplified": "检查更新失败",
            },
            # Help Tab Translations (expanded with full content)
            "help_title": {
                "english": "Kemono Downloader Guide",
                "japanese": "Kemono Downloader ガイド",
                "korean": "Kemono Downloader 안내서",
                "chinese-simplified": "Kemono Downloader 指南",
            },
            # Extension tab translations
            "extension_title": {
                "english": "Browser Extension",
                "japanese": "ブラウザ拡張機能",
                "korean": "브라우저 확장",
                "chinese-simplified": "浏览器扩展",
            },
            "tor_status_stopped": {
                "english": "Tor Status: Stopped",
                "japanese": "Torステータス: 停止中",
                "korean": "Tor 상태: 중지됨",
                "chinese-simplified": "Tor状态: 已停止",
            },
            "tor_status_starting": {
                "english": "Tor Status: Starting...",
                "japanese": "Torステータス: 開始中...",
                "korean": "Tor 상태: 시작 중...",
                "chinese-simplified": "Tor状态: 启动中...",
            },
            "tor_status_running": {
                "english": "Tor Status: Running",
                "japanese": "Torステータス: 実行中",
                "korean": "Tor 상태: 실행 중",
                "chinese-simplified": "Tor状态: 运行中",
            },
            "invalid_url_type": {
                "english": "Invalid URL type: {0}. Expected string.",
                "japanese": "無効なURLタイプ: {0}。文字列を期待します。",
                "korean": "잘못된 URL 유형: {0}. 문자열이 필요합니다.",
                "chinese-simplified": "无效的URL类型: {0}。应为字符串。",
            },
            "starting_detection_all_posts": {
                "english": "Starting detection of all posts in queue",
                "japanese": "キュー内のすべての投稿の検出を開始",
                "korean": "대기열의 모든 게시물 감지 시작",
                "chinese-simplified": "开始检测队列中的所有投稿",
            },
            "failed_fetch_post_no_response": {
                "english": "Failed to fetch post - No valid response",
                "japanese": "投稿の取得に失敗しました - 有効な応答がありません",
                "korean": "게시물 가져오기 실패 - 유효한 응답 없음",
                "chinese-simplified": "获取投稿失败 - 无有效响应",
            },
            "failed_fetch_post": {
                "english": "Failed to fetch post: {0}",
                "japanese": "投稿の取得に失敗しました: {0}",
                "korean": "게시물 가져오기 실패: {0}",
                "chinese-simplified": "获取投稿失败: {0}",
            },
            "failed_fetch_api_url_retry": {
                "english": "Failed to fetch {0} (attempt {1}/{2}). Retrying...",
                "japanese": "{0} の取得に失敗しました (試行 {1}/{2})。再試行中...",
                "korean": "{0} 가져오기 실패 (시도 {1}/{2}). 재시도 중...",
                "chinese-simplified": "获取 {0} 失败 (尝试 {1}/{2})。正在重试...",
            },
            "failed_fetch_api_url_final": {
                "english": "Failed to fetch {0} after {1} attempts",
                "japanese": "{1} 回の試行後に {0} の取得に失敗しました",
                "korean": "{1}번 시도 후 {0} 가져오기 실패",
                "chinese-simplified": "{1} 次尝试后获取 {0} 失败",
            },
            "failed_fetch_post_title": {
                "english": "Failed to fetch post title - No valid response",
                "japanese": "投稿タイトルの取得に失敗しました - 有効な応答がありません",
                "korean": "게시물 제목 가져오기 실패 - 유효한 응답 없음",
                "chinese-simplified": "获取投稿标题失败 - 无有效响应",
            },
            "error_fetching_post_info": {
                "english": "Error fetching post info: {0}",
                "japanese": "投稿情報の取得エラー: {0}",
                "korean": "게시물 정보 가져오기 오류: {0}",
                "chinese-simplified": "获取投稿信息时出错: {0}",
            },
            "error_fetching_post_retry": {
                "english": "Error fetching post {0} (attempt {1}/{2}): {3}. Retrying...",
                "japanese": "投稿 {0} の取得エラー (試行 {1}/{2}): {3}。再試行中...",
                "korean": "게시물 {0} 가져오기 오류 (시도 {1}/{2}): {3}. 재시도 중...",
                "chinese-simplified": "获取投稿 {0} 时出错 (尝试 {1}/{2}): {3}。正在重试...",
            },
            "error_fetching_post_final": {
                "english": "Error fetching post {0} after {1} attempts: {2}",
                "japanese": "{1} 回の試行後に投稿 {0} の取得エラーが発生しました: {2}",
                "korean": "{1}번 시도 후 게시물 {0} 가져오기 오류: {2}",
                "chinese-simplified": "{1} 次尝试后获取投稿 {0} 时出错: {2}",
            },
            "no_post_currently_viewed": {
                "english": "No post currently viewed to download.",
                "japanese": "現在表示中の投稿がダウンロード用にありません。",
                "korean": "현재 보고 있는 게시물이 다운로드할 수 없습니다.",
                "chinese-simplified": "当前没有查看的投稿可供下载。",
            },
            "no_more_urls_process": {
                "english": "No more URLs to process. Finishing download.",
                "japanese": "処理するURLがありません。ダウンロードを終了します。",
                "korean": "처리할 URL이 더 이상 없습니다. 다운로드를 완료합니다.",
                "chinese-simplified": "没有更多URL需要处理。完成下载。",
            },
            "no_more_posts_download": {
                "english": "No more posts to download. Finishing.",
                "japanese": "ダウンロードする投稿がありません。終了します。",
                "korean": "다운로드할 게시물이 더 이상 없습니다. 완료합니다.",
                "chinese-simplified": "没有更多投稿需要下载。完成。",
            },
            "thread_not_found_active": {
                "english": "Thread not found in active_threads.",
                "japanese": "active_threadsにスレッドが見つかりません。",
                "korean": "active_threads에서 스레드를 찾을 수 없습니다.",
                "chinese-simplified": "在active_threads中找不到线程。",
            },
            "no_active_download_threads": {
                "english": "No active DownloadThreads remaining. Proceeding to next post.",
                "japanese": "アクティブなDownloadThreadsが残っていません。次の投稿に進みます。",
                "korean": "활성 DownloadThreads가 남아 있지 않습니다. 다음 게시물로 진행합니다.",
                "chinese-simplified": "没有剩余的活跃DownloadThreads。继续下一个投稿。",
            },
            "processing_next_post": {
                "english": "Processing next post. Remaining URLs: {0}",
                "japanese": "次の投稿を処理中。残りのURL: {0}",
                "korean": "다음 게시물 처리 중. 남은 URL: {0}",
                "chinese-simplified": "正在处理下一个投稿。剩余URL: {0}",
            },
            "cleaning_up_thread": {
                "english": "Cleaning up thread for post. Remaining URLs: {0}",
                "japanese": "投稿のスレッドをクリーンアップ中。残りのURL: {0}",
                "korean": "게시물의 스레드 정리 중. 남은 URL: {0}",
                "chinese-simplified": "正在清理投稿线程。剩余URL: {0}",
            },
            "removed_thread_active": {
                "english": "Removed thread from active_threads. Active threads remaining: {0}",
                "japanese": "active_threadsからスレッドを削除しました。残りのアクティブスレッド: {0}",
                "korean": "active_threads에서 스레드를 제거했습니다. 남은 활성 스레드: {0}",
                "chinese-simplified": "从active_threads中移除线程。剩余活跃线程: {0}",
            },
            "active_download_threads_remaining": {
                "english": "Active DownloadThreads remaining: {0}",
                "japanese": "残りのアクティブDownloadThreads: {0}",
                "korean": "남은 활성 DownloadThreads: {0}",
                "chinese-simplified": "剩余活跃DownloadThreads: {0}",
            },
            "active_download_threads_running": {
                "english": "Active DownloadThreads still running: {0}. Waiting before proceeding.",
                "japanese": "アクティブDownloadThreadsがまだ実行中: {0}。続行前に待機します。",
                "korean": "활성 DownloadThreads가 아직 실행 중: {0}. 진행하기 전에 대기합니다.",
                "chinese-simplified": "活跃DownloadThreads仍在运行: {0}。继续前等待。",
            },
            "check_all_toggled": {
                "english": "Check ALL toggled to {0} for {1} visible files",
                "japanese": "{1} 個の表示ファイルに対してチェックALLが {0} に切り替えられました",
                "korean": "{1}개의 표시 파일에 대해 체크 ALL이 {0}으로 전환되었습니다",
                "chinese-simplified": "为 {1} 个可见文件切换了全选到 {0}",
            },
            "post_detection_cancellation": {
                "english": "PostDetectionThread cancellation initiated",
                "japanese": "PostDetectionThreadのキャンセルが開始されました",
                "korean": "PostDetectionThread 취소가 시작되었습니다",
                "chinese-simplified": "PostDetectionThread取消已启动",
            },
            "expand_logs": {
                "english": "Expand Logs",
                "japanese": "ログを展開",
                "korean": "로그 확장",
                "chinese-simplified": "展开日志",
            },
            "total_detected_posts": {
                "english": "Total detected posts: {0}",
                "japanese": "検出された投稿の総数: {0}",
                "korean": "감지된 총 게시물 수: {0}",
                "chinese-simplified": "检测到的总投稿数: {0}",
            },
            "displayed_files_for_post": {
                "english": "Displayed files for post {0}",
                "japanese": "投稿 {0} のファイルを表示しました",
                "korean": "게시물 {0}의 파일 표시됨",
                "chinese-simplified": "显示了投稿 {0} 的文件",
            },
            "files_detected_so_far": {
                "english": "Files detected so far: {0}",
                "japanese": "これまでに検出されたファイル: {0}",
                "korean": "지금까지 감지된 파일: {0}",
                "chinese-simplified": "迄今检测到的文件: {0}",
            },
            "finished_checking_all_posts": {
                "english": "Finished checking all posts. Total posts: {0}, Total files: {1}",
                "japanese": "すべての投稿のチェックが完了しました。総投稿数: {0}、総ファイル数: {1}",
                "korean": "모든 게시물 확인 완료. 총 게시물: {0}, 총 파일: {1}",
                "chinese-simplified": "完成检查所有投稿。总投稿数: {0}，总文件数: {1}",
            },
            "checked_files_for_download": {
                "english": "Checked files for download: {0}",
                "japanese": "ダウンロード用にチェックされたファイル: {0}",
                "korean": "다운로드용으로 체크된 파일: {0}",
                "chinese-simplified": "为下载选中的文件: {0}",
            },
            "preparing_files_for_urls": {
                "english": "Preparing files for URLs: {0}",
                "japanese": "URLのファイルを準備中: {0}",
                "korean": "URL에 대한 파일 준비 중: {0}",
                "chinese-simplified": "正在准备URL的文件: {0}",
            },
            "no_posts_available_download": {
                "english": "No posts available for download in URLs: {0}. Skipping to next.",
                "japanese": "URL {0} でダウンロード可能な投稿がありません。次にスキップします。",
                "korean": "URL {0}에서 다운로드 가능한 게시물이 없습니다. 다음으로 건너뜁니다.",
                "chinese-simplified": "URL {0} 中没有可下载的投稿。跳到下一个。",
            },
            "files_prepared_for_urls": {
                "english": "Files prepared for URLs: {0}, Total files: {1}",
                "japanese": "URL {0} のファイルが準備されました、総ファイル数: {1}",
                "korean": "URL {0}에 대한 파일 준비됨, 총 파일: {1}",
                "chinese-simplified": "为URL {0} 准备了文件，总文件数: {1}",
            },
            "updated_checked_urls": {
                "english": "Updated checked_urls after preparation: {0}",
                "japanese": "準備後にchecked_urlsを更新しました: {0}",
                "korean": "준비 후 checked_urls 업데이트됨: {0}",
                "chinese-simplified": "准备后更新了checked_urls: {0}",
            },
            "checked_files_after_filtering": {
                "english": "Checked files after filtering: {0}",
                "japanese": "フィルタリング後のチェック済みファイル: {0}",
                "korean": "필터링 후 체크된 파일: {0}",
                "chinese-simplified": "过滤后的选中文件: {0}",
            },
            "checked_files_list": {
                "english": "Checked files list: {0}",
                "japanese": "チェック済みファイルリスト: {0}",
                "korean": "체크된 파일 목록: {0}",
                "chinese-simplified": "选中文件列表: {0}",
            },
            "no_files_download_urls": {
                "english": "No files to download for URLs: {0}. Proceeding to next post.",
                "japanese": "URL {0} でダウンロードするファイルがありません。次の投稿に進みます。",
                "korean": "URL {0}에 대해 다운로드할 파일이 없습니다. 다음 게시물로 진행합니다.",
                "chinese-simplified": "URL {0} 没有要下载的文件。继续下一个投稿。",
            },
            "processing_post": {
                "english": "Processing post: {0}, Remaining URLs: {1}",
                "japanese": "投稿を処理中: {0}、残りのURL: {1}",
                "korean": "게시물 처리 중: {0}, 남은 URL: {1}",
                "chinese-simplified": "正在处理投稿: {0}，剩余URL: {1}",
            },
            "terminated_thread": {
                "english": "Terminated thread: {0}",
                "japanese": "スレッドを終了しました: {0}",
                "korean": "스레드 종료됨: {0}",
                "chinese-simplified": "终止线程: {0}",
            },
            "checkbox_toggled": {
                "english": "Checkbox toggled for {0} to {1}, checked_urls count: {2}",
                "japanese": "{0} のチェックボックスが {1} に切り替えられました、checked_urls数: {2}",
                "korean": "{0}의 체크박스가 {1}으로 전환됨, checked_urls 수: {2}",
                "chinese-simplified": "{0} 的复选框切换到 {1}，checked_urls 数量: {2}",
            },
            # ── Fast Mode & Multi-URL translations ──
            "fast_mode": {
                "english": "Fast Mode",
                "japanese": "高速モード",
                "korean": "빠른 모드",
                "chinese-simplified": "快速模式",
            },
            "fast_mode_info_title": {
                "english": "Fast Mode",
                "japanese": "高速モード",
                "korean": "빠른 모드",
                "chinese-simplified": "快速模式",
            },
            "fast_mode_info_text": {
                "english": (
                    "Normal Mode gives you full control — you add one URL at a time "
                    "and manually choose which file types to download (images, videos, "
                    "attachments, text, etc.).\n\n"
                    "Fast Mode is for when you just want everything downloaded quickly "
                    "with minimal clicks:\n\n"
                    "• All download categories are turned ON and locked, so nothing "
                    "gets missed\n"
                    "• A batch input area appears where you can paste many URLs at "
                    "once (one per line)\n"
                    "• Completed downloads are automatically removed from the queue\n\n"
                    "Turn it off at any time to go back to manual control."
                ),
                "japanese": (
                    "通常モードでは完全な制御が可能です — URLを1つずつ追加し、"
                    "ダウンロードするファイルの種類（画像、動画、添付ファイル、テキスト"
                    "など）を手動で選択します。\n\n"
                    "高速モードは、最小限の操作ですべてを素早くダウンロードしたい時に"
                    "使います：\n\n"
                    "• すべてのダウンロードカテゴリがONになりロックされるため、"
                    "何も見逃しません\n"
                    "• 一括入力エリアが表示され、多数のURLを一度に貼り付けられます"
                    "（1行に1つ）\n"
                    "• 完了したダウンロードはキューから自動的に削除されます\n\n"
                    "いつでもオフにして手動制御に戻せます。"
                ),
                "korean": (
                    "일반 모드에서는 완전한 제어가 가능합니다 — URL을 하나씩 추가하고 "
                    "다운로드할 파일 유형(이미지, 동영상, 첨부파일, 텍스트 등)을 "
                    "직접 선택합니다.\n\n"
                    "빠른 모드는 최소한의 클릭으로 모든 것을 빠르게 다운로드하고 싶을 때 "
                    "사용합니다:\n\n"
                    "• 모든 다운로드 카테고리가 켜지고 잠겨서 아무것도 놓치지 않습니다\n"
                    "• 일괄 입력 영역이 나타나 여러 URL을 한 번에 붙여넣을 수 있습니다"
                    "(한 줄에 하나)\n"
                    "• 완료된 다운로드는 큐에서 자동으로 제거됩니다\n\n"
                    "언제든지 끄면 수동 제어로 돌아갈 수 있습니다."
                ),
                "chinese-simplified": (
                    "普通模式让您完全控制 — 每次添加一个URL，手动选择要下载的文件"
                    "类型（图片、视频、附件、文本等）。\n\n"
                    "快速模式适用于您想以最少的点击快速下载所有内容的情况：\n\n"
                    "• 所有下载类别将被开启并锁定，确保不会遗漏任何内容\n"
                    "• 会出现批量输入区域，您可以一次粘贴多个URL（每行一个）\n"
                    "• 已完成的下载会自动从队列中移除\n\n"
                    "随时关闭即可恢复手动控制。"
                ),
            },
            "fast_mode_enabled": {
                "english": "Fast Mode enabled – all files will be downloaded, options locked.",
                "japanese": "高速モードが有効になりました – すべてのファイルがダウンロードされ、オプションがロックされます。",
                "korean": "빠른 모드가 활성화되었습니다 – 모든 파일이 다운로드되며 옵션이 잠겼습니다.",
                "chinese-simplified": "快速模式已启用 – 将下载所有文件，选项已锁定。",
            },
            "fast_mode_disabled": {
                "english": "Fast Mode disabled – manual control restored.",
                "japanese": "高速モードが無効になりました – 手動制御が復元されました。",
                "korean": "빠른 모드가 비활성화되었습니다 – 수동 제어가 복원되었습니다.",
                "chinese-simplified": "快速模式已禁用 – 手动控制已恢复。",
            },
            "fast_mode_removed_post_url": {
                "english": "Fast Mode: removed completed post {0} from queue.",
                "japanese": "高速モード: 完了した投稿 {0} をキューから削除しました。",
                "korean": "빠른 모드: 완료된 게시물 {0}을(를) 큐에서 제거했습니다.",
                "chinese-simplified": "快速模式：已从队列中移除已完成的帖子 {0}。",
            },
            "fast_mode_removed_posts": {
                "english": "Fast Mode: removed {0} completed post(s) from queue.",
                "japanese": "高速モード: 完了した{0}件の投稿をキューから削除しました。",
                "korean": "빠른 모드: 완료된 {0}개의 게시물을 큐에서 제거했습니다.",
                "chinese-simplified": "快速模式：已从队列中移除 {0} 个已完成的帖子。",
            },
            "fast_mode_removed_creator": {
                "english": "Fast Mode: removed completed creator {0} from queue.",
                "japanese": "高速モード: 完了したクリエイター {0} をキューから削除しました。",
                "korean": "빠른 모드: 완료된 크리에이터 {0}을(를) 큐에서 제거했습니다.",
                "chinese-simplified": "快速模式：已从队列中移除已完成的创作者 {0}。",
            },
            "fast_mode_batch_start": {
                "english": "Fast Mode: starting batch download for {0} creator(s).",
                "japanese": "高速モード: {0}人のクリエイターの一括ダウンロードを開始します。",
                "korean": "빠른 모드: {0}명의 크리에이터 일괄 다운로드를 시작합니다.",
                "chinese-simplified": "快速模式：开始批量下载 {0} 个创作者。",
            },
            "fast_mode_batch_complete": {
                "english": "Fast Mode: batch download complete.",
                "japanese": "高速モード: 一括ダウンロードが完了しました。",
                "korean": "빠른 모드: 일괄 다운로드가 완료되었습니다.",
                "chinese-simplified": "快速模式：批量下载完成。",
            },
            "fast_mode_processing_creator": {
                "english": "Fast Mode: processing creator {0} ({1} remaining).",
                "japanese": "高速モード: クリエイター {0} を処理中（残り {1} 件）。",
                "korean": "빠른 모드: 크리에이터 {0} 처리 중 (나머지 {1}개).",
                "chinese-simplified": "快速模式：正在处理创作者 {0}（剩余 {1} 个）。",
            },
            "fast_mode_no_posts_found": {
                "english": "Fast Mode: no posts found for creator {0}, skipping.",
                "japanese": "高速モード: クリエイター {0} の投稿が見つかりません。スキップします。",
                "korean": "빠른 모드: 크리에이터 {0}의 게시물을 찾을 수 없습니다. 건너뜁니다.",
                "chinese-simplified": "快速模式：未找到创作者 {0} 的帖子，跳过。",
            },
            "fast_mode_auto_selected": {
                "english": "Fast Mode: auto-selected {0} post(s) for {1}.",
                "japanese": "高速モード: {1} の {0} 件の投稿を自動選択しました。",
                "korean": "빠른 모드: {1}에 대해 {0}개의 게시물을 자동 선택했습니다.",
                "chinese-simplified": "快速模式：为 {1} 自动选择了 {0} 个帖子。",
            },
            "multi_url_placeholder": {
                "english": "Paste multiple post URLs here, one per line…",
                "japanese": "複数の投稿URLをここに貼り付けてください（1行に1つ）…",
                "korean": "여기에 여러 게시물 URL을 붙여넣으세요 (한 줄에 하나)…",
                "chinese-simplified": "在此粘贴多个帖子URL，每行一个…",
            },
            "multi_url_placeholder_creator": {
                "english": "Paste multiple creator URLs here, one per line…",
                "japanese": "複数のクリエイターURLをここに貼り付けてください（1行に1つ）…",
                "korean": "여기에 여러 크리에이터 URL을 붙여넣으세요 (한 줄에 하나)…",
                "chinese-simplified": "在此粘贴多个创作者URL，每行一个…",
            },
            "add_all_to_queue": {
                "english": "Add All to Queue",
                "japanese": "すべてキューに追加",
                "korean": "모두 큐에 추가",
                "chinese-simplified": "全部添加到队列",
            },
            "thumbnail_downloader_tab": {
                "english": "Thumbnail Downloader",
                "japanese": "サムネイルダウンローダー",
                "korean": "썸네일 다운로더",
                "chinese-simplified": "缩略图下载器",
            },
            "download_mode": {
                "english": "Download Mode:",
                "japanese": "ダウンロードモード:",
                "korean": "다운로드 모드:",
                "chinese-simplified": "下载模式：",
            },
            "post_mode": {
                "english": "Post",
                "japanese": "投稿",
                "korean": "포스트",
                "chinese-simplified": "帖子",
            },
            "creator_mode": {
                "english": "Creator",
                "japanese": "クリエイター",
                "korean": "크리에이터",
                "chinese-simplified": "创作者",
            },
            "mixed_links_error": {
                "english": "Post and Creator links cannot be mixed in the queue.",
                "japanese": "投稿とクリエイターのリンクをキュー内で混在させることはできません。",
                "korean": "대기열에서 포스트와 크리에이터 링크를 혼합할 수 없습니다.",
                "chinese-simplified": "队列中不能混合帖子和创作者链接。",
            },
            "no_thumbnails_found": {
                "english": "No thumbnails found for the given link(s).",
                "japanese": "指定されたリンクのサムネイルが見つかりませんでした。",
                "korean": "주어진 링크에 대한 썸네일을 찾을 수 없습니다.",
                "chinese-simplified": "未找到指定链接的缩略图。",
            },
            "detect_thumbnails": {
                "english": "Detect Thumbnails",
                "japanese": "サムネイルを検出",
                "korean": "썸네일 감지",
                "chinese-simplified": "检测缩略图",
            },
            "detecting_thumbnails": {
                "english": "Detecting thumbnails...",
                "japanese": "サムネイルを検出中...",
                "korean": "썸네일 감지 중...",
                "chinese-simplified": "正在检测缩略图...",
            },
            "thumbnails_detected": {
                "english": "Detected {0} thumbnail(s).",
                "japanese": "{0} 件のサムネイルを検出しました。",
                "korean": "{0}개의 썸네일을 감지했습니다.",
                "chinese-simplified": "已检测到 {0} 个缩略图。",
            },
            "downloading_thumbnails": {
                "english": "Downloading thumbnails...",
                "japanese": "サムネイルをダウンロード中...",
                "korean": "썸네일 다운로드 중...",
                "chinese-simplified": "正在下载缩略图...",
            },
            "thumbnails_downloaded": {
                "english": "Downloaded {0} thumbnail(s).",
                "japanese": "{0} 件のサムネイルをダウンロードしました。",
                "korean": "{0}개의 썸네일을 다운로드했습니다.",
                "chinese-simplified": "已下载 {0} 个缩略图。",
            },
            "thumbnail_queue_placeholder": {
                "english": "Enter Post or Creator URL here...",
                "japanese": "ここに投稿またはクリエイターのURLを入力...",
                "korean": "여기에 포스트 또는 크리에이터 URL 입력...",
                "chinese-simplified": "在此输入帖子或创作者 URL...",
            },
            "thumbnails_to_download": {
                "english": "Thumbnails to Download",
                "japanese": "ダウンロードするサムネイル",
                "korean": "다운로드할 썸네일",
                "chinese-simplified": "要下载的缩略图",
            },
            "filter_placeholder": {
                "english": "Filter thumbnails...",
                "japanese": "サムネイルをフィルター...",
                "korean": "썸네일 필터링...",
                "chinese-simplified": "过滤缩略图...",
            },
            "selected_count": {
                "english": "Selected: {0} / {1}",
                "japanese": "選択済み: {0} / {1}",
                "korean": "선택됨: {0} / {1}",
                "chinese-simplified": "已选择：{0} / {1}",
            },
            "log_console": {
                "english": "Log Console",
                "japanese": "ログコンソール",
                "korean": "로그 콘솔",
                "chinese-simplified": "日志控制台",
            },
            "start_download": {
                "english": "Start Download",
                "japanese": "ダウンロード開始",
                "korean": "다운로드 시작",
                "chinese-simplified": "开始下载",
            },
            "remove": {
                "english": "Remove",
                "japanese": "削除",
                "korean": "제거",
                "chinese-simplified": "移除",
            },
            "clear": {
                "english": "Clear",
                "japanese": "クリア",
                "korean": "지우기",
                "chinese-simplified": "清除",
            },
            "skip_existing_files": {
                "english": "Skip existing files",
                "japanese": "既存のファイルをスキップ",
                "korean": "기존 파일 건너뛰기",
                "chinese-simplified": "跳过已存在的文件",
            },
            "mode_switch_warning_title": {
                "english": "Mode Change Warning",
                "japanese": "モード変更の警告",
                "korean": "모드 변경 경고",
                "chinese-simplified": "模式更改警告",
            },
            "mode_switch_warning_msg": {
                "english": "Switching download mode will clear the current queue. Do you want to proceed?",
                "japanese": "ダウンロードモードを切り替えると現在のキューがクリアされます。続行しますか？",
                "korean": "다운로드 모드를 전환하면 현재 대기열이 삭제됩니다. 진행하시겠습니까?",
                "chinese-simplified": "切换下载模式将清除当前队列。您要继续吗？",
            },
            "no_items_selected_download": {
                "english": "No thumbnails selected for download.",
                "japanese": "ダウンロードするサムネイルが選択されていません。",
                "korean": "다운로드할 썸네일이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的缩略图。",
            },
            # History tab and favorites
            "warning": {
                "english": "Warning",
                "japanese": "警告",
                "korean": "경고",
                "chinese-simplified": "警告",
            },
            "information": {
                "english": "Information",
                "japanese": "情報",
                "korean": "정보",
                "chinese-simplified": "信息",
            },
            "info": {
                "english": "Information",
                "japanese": "情報",
                "korean": "정보",
                "chinese-simplified": "信息",
            },
            "success": {
                "english": "Success",
                "japanese": "成功",
                "korean": "성공",
                "chinese-simplified": "成功",
            },
            "directory_creation_failed": {
                "english": "Could not create the directory: {0}",
                "japanese": "ディレクトリを作成できませんでした：{0}",
                "korean": "디렉터리를 만들 수 없습니다: {0}",
                "chinese-simplified": "无法创建目录：{0}",
            },
            "incremental_filtering_added_posts": {
                "english": "Added {0} posts to the list",
                "japanese": "リストに {0} 件の投稿を追加しました",
                "korean": "목록에 게시물 {0}개를 추가했습니다",
                "chinese-simplified": "已向列表添加 {0} 个帖子",
            },
            "history_tab": {
                "english": "History",
                "japanese": "履歴",
                "korean": "기록",
                "chinese-simplified": "历史记录",
            },
            "history_downloads_view": {
                "english": "Download History",
                "japanese": "ダウンロード履歴",
                "korean": "다운로드 기록",
                "chinese-simplified": "下载历史",
            },
            "favorites_view": {
                "english": "Favorites",
                "japanese": "お気に入り",
                "korean": "즐겨찾기",
                "chinese-simplified": "收藏夹",
            },
            "history_search_placeholder": {
                "english": "Search titles, links, creators...",
                "japanese": "タイトル、リンク、クリエイターを検索...",
                "korean": "제목, 링크, 크리에이터 검색...",
                "chinese-simplified": "搜索标题、链接、创作者...",
            },
            "history_filter_all": {
                "english": "All types",
                "japanese": "すべての種類",
                "korean": "모든 유형",
                "chinese-simplified": "所有类型",
            },
            "history_type_post": {
                "english": "Post",
                "japanese": "投稿",
                "korean": "게시물",
                "chinese-simplified": "帖子",
            },
            "history_type_creator": {
                "english": "Creator",
                "japanese": "クリエイター",
                "korean": "크리에이터",
                "chinese-simplified": "创作者",
            },
            "history_type_thumbnail": {
                "english": "Thumbnails",
                "japanese": "サムネイル",
                "korean": "썸네일",
                "chinese-simplified": "缩略图",
            },
            "history_status_completed": {
                "english": "Completed",
                "japanese": "完了",
                "korean": "완료",
                "chinese-simplified": "已完成",
            },
            "history_status_partial": {
                "english": "Partial",
                "japanese": "一部完了",
                "korean": "일부 완료",
                "chinese-simplified": "部分完成",
            },
            "history_status_failed": {
                "english": "Failed",
                "japanese": "失敗",
                "korean": "실패",
                "chinese-simplified": "失败",
            },
            "history_status_cancelled": {
                "english": "Cancelled",
                "japanese": "キャンセル",
                "korean": "취소됨",
                "chinese-simplified": "已取消",
            },
            "history_col_date": {
                "english": "Date",
                "japanese": "日時",
                "korean": "날짜",
                "chinese-simplified": "日期",
            },
            "history_col_type": {
                "english": "Type",
                "japanese": "種類",
                "korean": "유형",
                "chinese-simplified": "类型",
            },
            "history_col_title": {
                "english": "Title",
                "japanese": "タイトル",
                "korean": "제목",
                "chinese-simplified": "标题",
            },
            "history_col_files": {
                "english": "Files",
                "japanese": "ファイル",
                "korean": "파일",
                "chinese-simplified": "文件",
            },
            "history_col_posts": {
                "english": "Posts",
                "japanese": "投稿",
                "korean": "게시물",
                "chinese-simplified": "帖子",
            },
            "history_col_size": {
                "english": "Size",
                "japanese": "サイズ",
                "korean": "크기",
                "chinese-simplified": "大小",
            },
            "history_col_duration": {
                "english": "Duration",
                "japanese": "所要時間",
                "korean": "소요 시간",
                "chinese-simplified": "用时",
            },
            "history_col_status": {
                "english": "Status",
                "japanese": "状態",
                "korean": "상태",
                "chinese-simplified": "状态",
            },
            "history_col_folder": {
                "english": "Folder",
                "japanese": "フォルダー",
                "korean": "폴더",
                "chinese-simplified": "文件夹",
            },
            "history_col_link": {
                "english": "Link",
                "japanese": "リンク",
                "korean": "링크",
                "chinese-simplified": "链接",
            },
            "history_folder_ok": {
                "english": "Available",
                "japanese": "あり",
                "korean": "있음",
                "chinese-simplified": "可用",
            },
            "history_folder_missing": {
                "english": "Missing",
                "japanese": "見つかりません",
                "korean": "없음",
                "chinese-simplified": "缺失",
            },
            "history_folder_unknown": {
                "english": "Not recorded",
                "japanese": "記録なし",
                "korean": "기록 없음",
                "chinese-simplified": "未记录",
            },
            "history_summary": {
                "english": "{0} downloads · {1} files ({2} failed) · {3} posts · {4}",
                "japanese": "{0} 件のダウンロード · {1} ファイル（失敗 {2}）· {3} 投稿 · {4}",
                "korean": "다운로드 {0}건 · 파일 {1}개 (실패 {2}) · 게시물 {3}개 · {4}",
                "chinese-simplified": "{0} 次下载 · {1} 个文件（失败 {2}）· {3} 个帖子 · {4}",
            },
            "history_record_toggle": {
                "english": "Record download history",
                "japanese": "ダウンロード履歴を記録",
                "korean": "다운로드 기록 저장",
                "chinese-simplified": "记录下载历史",
            },
            "history_open_folder": {
                "english": "Open Folder",
                "japanese": "フォルダーを開く",
                "korean": "폴더 열기",
                "chinese-simplified": "打开文件夹",
            },
            "history_copy_link": {
                "english": "Copy Link",
                "japanese": "リンクをコピー",
                "korean": "링크 복사",
                "chinese-simplified": "复制链接",
            },
            "history_add_to_queue": {
                "english": "Add to Queue",
                "japanese": "キューに追加",
                "korean": "대기열에 추가",
                "chinese-simplified": "添加到队列",
            },
            "history_add_favorite": {
                "english": "Add to Favorites",
                "japanese": "お気に入りに追加",
                "korean": "즐겨찾기에 추가",
                "chinese-simplified": "添加到收藏夹",
            },
            "history_remove": {
                "english": "Remove",
                "japanese": "削除",
                "korean": "삭제",
                "chinese-simplified": "删除",
            },
            "history_clear": {
                "english": "Clear History",
                "japanese": "履歴を消去",
                "korean": "기록 지우기",
                "chinese-simplified": "清除历史",
            },
            "history_export": {
                "english": "Export CSV",
                "japanese": "CSVにエクスポート",
                "korean": "CSV로 내보내기",
                "chinese-simplified": "导出 CSV",
            },
            "history_clear_confirm": {
                "english": "Delete all {0} history entries? Your downloaded files are not affected.",
                "japanese": "履歴 {0} 件をすべて削除しますか？ダウンロード済みのファイルは削除されません。",
                "korean": "기록 {0}건을 모두 삭제하시겠습니까? 다운로드한 파일은 삭제되지 않습니다.",
                "chinese-simplified": "删除全部 {0} 条历史记录？已下载的文件不受影响。",
            },
            "history_remove_confirm": {
                "english": "Remove {0} selected entries from history? Your downloaded files are not affected.",
                "japanese": "選択した {0} 件を履歴から削除しますか？ダウンロード済みのファイルは削除されません。",
                "korean": "선택한 {0}건을 기록에서 삭제하시겠습니까? 다운로드한 파일은 삭제되지 않습니다.",
                "chinese-simplified": "从历史中删除所选的 {0} 条记录？已下载的文件不受影响。",
            },
            "history_folder_missing_title": {
                "english": "Folder Not Found",
                "japanese": "フォルダーが見つかりません",
                "korean": "폴더를 찾을 수 없음",
                "chinese-simplified": "找不到文件夹",
            },
            "history_folder_missing_message": {
                "english": "This download's folder no longer exists:\n{0}\n\nIt may have been moved, renamed or deleted.",
                "japanese": "このダウンロードのフォルダーは存在しません：\n{0}\n\n移動、名前の変更、または削除された可能性があります。",
                "korean": "이 다운로드의 폴더가 더 이상 존재하지 않습니다:\n{0}\n\n이동되었거나 이름이 바뀌었거나 삭제되었을 수 있습니다.",
                "chinese-simplified": "此下载的文件夹已不存在：\n{0}\n\n它可能已被移动、重命名或删除。",
            },
            "history_locate_folder": {
                "english": "Locate Folder...",
                "japanese": "フォルダーを指定...",
                "korean": "폴더 찾기...",
                "chinese-simplified": "定位文件夹...",
            },
            "history_open_parent": {
                "english": "Open Parent Folder",
                "japanese": "親フォルダーを開く",
                "korean": "상위 폴더 열기",
                "chinese-simplified": "打开上级文件夹",
            },
            "history_redownload": {
                "english": "Download Again",
                "japanese": "再ダウンロード",
                "korean": "다시 다운로드",
                "chinese-simplified": "重新下载",
            },
            "history_no_folder": {
                "english": "No folder was recorded for this download.",
                "japanese": "このダウンロードにはフォルダーが記録されていません。",
                "korean": "이 다운로드에는 기록된 폴더가 없습니다.",
                "chinese-simplified": "此下载没有记录文件夹。",
            },
            "history_select_entry": {
                "english": "Select an entry first.",
                "japanese": "先に項目を選択してください。",
                "korean": "먼저 항목을 선택하세요.",
                "chinese-simplified": "请先选择一项。",
            },
            "history_storage_error": {
                "english": "History can't be saved to disk ({0}). It will be kept only until the app closes.",
                "japanese": "履歴をディスクに保存できません（{0}）。アプリを閉じるまでの間だけ保持されます。",
                "korean": "기록을 디스크에 저장할 수 없습니다({0}). 앱을 닫을 때까지만 유지됩니다.",
                "chinese-simplified": "无法将历史记录保存到磁盘（{0}）。仅在应用关闭前保留。",
            },
            "history_empty": {
                "english": "No downloads recorded yet.\nFinished post, creator and thumbnail downloads will appear here.",
                "japanese": "まだダウンロードの記録はありません。\n完了した投稿・クリエイター・サムネイルのダウンロードがここに表示されます。",
                "korean": "아직 기록된 다운로드가 없습니다.\n완료된 게시물, 크리에이터, 썸네일 다운로드가 여기에 표시됩니다.",
                "chinese-simplified": "尚无下载记录。\n已完成的帖子、创作者和缩略图下载将显示在这里。",
            },
            "history_exported": {
                "english": "Exported {0} entries to {1}",
                "japanese": "{0} 件を {1} にエクスポートしました",
                "korean": "{0}건을 {1}(으)로 내보냈습니다",
                "chinese-simplified": "已将 {0} 条记录导出到 {1}",
            },
            "history_export_failed": {
                "english": "Export failed: {0}",
                "japanese": "エクスポートに失敗しました：{0}",
                "korean": "내보내기 실패: {0}",
                "chinese-simplified": "导出失败：{0}",
            },
            "history_copied": {
                "english": "Copied {0} link(s)",
                "japanese": "{0} 件のリンクをコピーしました",
                "korean": "링크 {0}개를 복사했습니다",
                "chinese-simplified": "已复制 {0} 个链接",
            },
            "history_queued": {
                "english": "Added {0} link(s) to the queue",
                "japanese": "{0} 件のリンクをキューに追加しました",
                "korean": "링크 {0}개를 대기열에 추가했습니다",
                "chinese-simplified": "已将 {0} 个链接添加到队列",
            },
            "history_queue_busy": {
                "english": "That tab is busy downloading; try again when it finishes",
                "japanese": "そのタブはダウンロード中です。完了後にもう一度お試しください",
                "korean": "해당 탭이 다운로드 중입니다. 완료된 후 다시 시도하세요",
                "chinese-simplified": "该选项卡正在下载，请在完成后重试",
            },
            "history_queue_duplicate": {
                "english": "Already in the queue: {0}",
                "japanese": "すでにキューにあります：{0}",
                "korean": "이미 대기열에 있습니다: {0}",
                "chinese-simplified": "已在队列中：{0}",
            },
            "history_queue_mode_mismatch": {
                "english": "The thumbnail queue holds the other kind of link; clear it first",
                "japanese": "サムネイルのキューには別の種類のリンクがあります。先にクリアしてください",
                "korean": "썸네일 대기열에 다른 종류의 링크가 있습니다. 먼저 비우세요",
                "chinese-simplified": "缩略图队列中是另一种链接，请先清空",
            },
            "library_invalid_link": {
                "english": "Not a supported post or creator link: {0}",
                "japanese": "対応していない投稿・クリエイターのリンクです：{0}",
                "korean": "지원되지 않는 게시물 또는 크리에이터 링크입니다: {0}",
                "chinese-simplified": "不是受支持的帖子或创作者链接：{0}",
            },
            "favorites_add_placeholder": {
                "english": "Paste a post or creator link to save it",
                "japanese": "保存する投稿またはクリエイターのリンクを貼り付け",
                "korean": "저장할 게시물 또는 크리에이터 링크를 붙여넣으세요",
                "chinese-simplified": "粘贴要保存的帖子或创作者链接",
            },
            "favorites_add": {
                "english": "Save",
                "japanese": "保存",
                "korean": "저장",
                "chinese-simplified": "保存",
            },
            "favorites_col_title": {
                "english": "Title",
                "japanese": "タイトル",
                "korean": "제목",
                "chinese-simplified": "标题",
            },
            "favorites_col_note": {
                "english": "Note",
                "japanese": "メモ",
                "korean": "메모",
                "chinese-simplified": "备注",
            },
            "favorites_col_added": {
                "english": "Added",
                "japanese": "追加日時",
                "korean": "추가한 날짜",
                "chinese-simplified": "添加时间",
            },
            "favorites_col_last_download": {
                "english": "Last Downloaded",
                "japanese": "最終ダウンロード",
                "korean": "마지막 다운로드",
                "chinese-simplified": "上次下载",
            },
            "favorites_never": {
                "english": "Never",
                "japanese": "なし",
                "korean": "없음",
                "chinese-simplified": "从未",
            },
            "favorites_open_browser": {
                "english": "Open in Browser",
                "japanese": "ブラウザーで開く",
                "korean": "브라우저에서 열기",
                "chinese-simplified": "在浏览器中打开",
            },
            "favorites_import": {
                "english": "Import TXT",
                "japanese": "TXTをインポート",
                "korean": "TXT 가져오기",
                "chinese-simplified": "导入 TXT",
            },
            "favorites_export": {
                "english": "Export TXT",
                "japanese": "TXTにエクスポート",
                "korean": "TXT로 내보내기",
                "chinese-simplified": "导出 TXT",
            },
            "favorites_added": {
                "english": "Saved to favorites: {0}",
                "japanese": "お気に入りに保存しました：{0}",
                "korean": "즐겨찾기에 저장했습니다: {0}",
                "chinese-simplified": "已保存到收藏夹：{0}",
            },
            "favorites_added_count": {
                "english": "Saved {0} link(s) to favorites",
                "japanese": "{0} 件のリンクをお気に入りに保存しました",
                "korean": "링크 {0}개를 즐겨찾기에 저장했습니다",
                "chinese-simplified": "已将 {0} 个链接保存到收藏夹",
            },
            "favorites_already": {
                "english": "Already in favorites: {0}",
                "japanese": "すでにお気に入りにあります：{0}",
                "korean": "이미 즐겨찾기에 있습니다: {0}",
                "chinese-simplified": "已在收藏夹中：{0}",
            },
            "favorites_remove_confirm": {
                "english": "Remove {0} selected favorites?",
                "japanese": "選択した {0} 件のお気に入りを削除しますか？",
                "korean": "선택한 즐겨찾기 {0}개를 삭제하시겠습니까?",
                "chinese-simplified": "删除所选的 {0} 个收藏？",
            },
            "favorites_empty": {
                "english": "No favorites yet.\nUse the star button in the Post or Creator tab, or paste a link above.",
                "japanese": "お気に入りはまだありません。\n投稿・クリエイタータブの星ボタンを使うか、上にリンクを貼り付けてください。",
                "korean": "아직 즐겨찾기가 없습니다.\n게시물 또는 크리에이터 탭의 별 버튼을 사용하거나 위에 링크를 붙여넣으세요.",
                "chinese-simplified": "尚无收藏。\n使用帖子或创作者选项卡中的星形按钮，或在上方粘贴链接。",
            },
            "favorites_imported": {
                "english": "Imported {0} link(s), skipped {1}",
                "japanese": "{0} 件をインポート、{1} 件をスキップしました",
                "korean": "{0}개를 가져오고 {1}개를 건너뛰었습니다",
                "chinese-simplified": "已导入 {0} 个链接，跳过 {1} 个",
            },
            "bookmark_button_tooltip": {
                "english": "Save the link in the box (or the one you're viewing) to Favorites",
                "japanese": "入力欄のリンク（または表示中のリンク）をお気に入りに保存",
                "korean": "입력란의 링크(또는 보고 있는 링크)를 즐겨찾기에 저장",
                "chinese-simplified": "将输入框中的链接（或正在查看的链接）保存到收藏夹",
            },
            "bookmark_no_link": {
                "english": "Enter a link or view one first to save it to Favorites",
                "japanese": "お気に入りに保存するには、先にリンクを入力するか表示してください",
                "korean": "즐겨찾기에 저장하려면 먼저 링크를 입력하거나 여세요",
                "chinese-simplified": "请先输入或查看一个链接，再保存到收藏夹",
            },
            "unexpected_error_title": {
                "english": "Unexpected Error",
                "japanese": "予期しないエラー",
                "korean": "예기치 않은 오류",
                "chinese-simplified": "意外错误",
            },
            "unexpected_error_text": {
                "english": "Something went wrong, but Kemono Downloader is still running. If something stops working, restart the app. To report the problem, open an issue on GitHub and include the error details.",
                "japanese": "問題が発生しましたが、Kemono Downloaderは引き続き動作しています。動作がおかしい場合はアプリを再起動してください。問題を報告するには、GitHubでIssueを作成し、エラーの詳細を添えてください。",
                "korean": "문제가 발생했지만 Kemono Downloader는 계속 실행 중입니다. 제대로 작동하지 않으면 앱을 다시 시작하세요. 문제를 신고하려면 GitHub에서 이슈를 열고 오류 세부 정보를 첨부하세요.",
                "chinese-simplified": "出现了问题，但 Kemono Downloader 仍在运行。如果某些功能无法正常工作，请重新启动应用。如需报告此问题，请在 GitHub 上创建 Issue 并附上错误详情。",
            },
            "tor_checksum_mismatch": {
                "english": "The downloaded Tor package doesn't match its published checksum, so it was not installed. Please try again later.",
                "japanese": "ダウンロードしたTorパッケージが公開されているチェックサムと一致しないため、インストールしませんでした。しばらくしてからもう一度お試しください。",
                "korean": "다운로드한 Tor 패키지가 공개된 체크섬과 일치하지 않아 설치하지 않았습니다. 나중에 다시 시도하세요.",
                "chinese-simplified": "下载的 Tor 软件包与公布的校验和不匹配，因此未安装。请稍后重试。",
            },
            "help_button": {
                "english": "Help",
                "japanese": "ヘルプ",
                "korean": "도움말",
                "chinese-simplified": "帮助",
            },
            "custom_proxy": {
                "english": "Custom Proxy",
                "japanese": "カスタムプロキシ",
                "korean": "사용자 지정 프록시",
                "chinese-simplified": "自定义代理",
            },
            "tor_help_title": {
                "english": "Tor Setup Help",
                "japanese": "Torセットアップのヘルプ",
                "korean": "Tor 설정 도움말",
                "chinese-simplified": "Tor 设置帮助",
            },
            "tor_help_text": {
                "english": "<b>How to set up Tor for downloading:</b><br><br>1. Click <b>Download Tor</b> to download the Tor Expert Bundle (the Tor program, without the Tor Browser).<br>2. Wait for the download to finish.<br>3. Click <b>Start Tor</b> to start the Tor process.<br>4. Click <b>Test Tor</b> to check that Tor is working.<br>5. Tick <b>Use Proxy</b> with <b>Tor</b> selected, then start downloading.<br><br><b>Note:</b> Tor provides anonymity but is usually slower than a direct connection. While Tor is selected, downloads only go through Tor: if Tor isn't running, they fail instead of connecting directly.",
                "japanese": "<b>ダウンロードにTorを設定する方法:</b><br><br>1. <b>Torをダウンロード</b>をクリックして、Tor Expert Bundle（Tor Browserを含まないTor本体）をダウンロードします。<br>2. ダウンロードが完了するまで待ちます。<br>3. <b>Torを開始</b>をクリックしてTorプロセスを起動します。<br>4. <b>Torをテスト</b>をクリックしてTorが動作していることを確認します。<br>5. <b>Tor</b>を選択した状態で<b>プロキシを使用</b>にチェックを入れ、ダウンロードを開始します。<br><br><b>注意:</b> Torは匿名性を提供しますが、通常は直接接続より遅くなります。Torを選択している間、ダウンロードはTor経由でのみ行われます。Torが起動していない場合は、直接接続せずに失敗します。",
                "korean": "<b>다운로드에 Tor를 설정하는 방법:</b><br><br>1. <b>Tor 다운로드</b>를 클릭하여 Tor Expert Bundle(Tor Browser를 제외한 Tor 프로그램)을 다운로드합니다.<br>2. 다운로드가 끝날 때까지 기다립니다.<br>3. <b>Tor 시작</b>을 클릭하여 Tor 프로세스를 시작합니다.<br>4. <b>Tor 테스트</b>를 클릭하여 Tor가 작동하는지 확인합니다.<br>5. <b>Tor</b>를 선택한 상태에서 <b>프록시 사용</b>을 체크한 다음 다운로드를 시작합니다.<br><br><b>참고:</b> Tor는 익명성을 제공하지만 보통 직접 연결보다 느립니다. Tor를 선택한 동안에는 다운로드가 Tor를 통해서만 이루어지며, Tor가 실행 중이 아니면 직접 연결하지 않고 실패합니다.",
                "chinese-simplified": "<b>如何设置 Tor 进行下载：</b><br><br>1. 点击<b>下载Tor</b>，下载 Tor Expert Bundle（不含 Tor 浏览器的 Tor 程序）。<br>2. 等待下载完成。<br>3. 点击<b>启动Tor</b>启动 Tor 进程。<br>4. 点击<b>测试Tor</b>确认 Tor 正常工作。<br>5. 选择 <b>Tor</b> 并勾选<b>使用代理</b>，然后开始下载。<br><br><b>注意：</b>Tor 提供匿名性，但通常比直接连接慢。选择 Tor 时，下载只会通过 Tor 进行：如果 Tor 未运行，下载会失败，而不会直接连接。",
            },
            "could_not_create_directory": {
                "english": "Could not create directory: {0}",
                "japanese": "ディレクトリを作成できませんでした: {0}",
                "korean": "디렉터리를 만들 수 없습니다: {0}",
                "chinese-simplified": "无法创建目录：{0}",
            },
            "could_not_open_directory": {
                "english": "Could not open directory: {0}",
                "japanese": "ディレクトリを開けませんでした: {0}",
                "korean": "디렉터리를 열 수 없습니다: {0}",
                "chinese-simplified": "无法打开目录：{0}",
            },
            "no_logs_to_save": {
                "english": "There are no logs to save yet.",
                "japanese": "保存するログはまだありません。",
                "korean": "아직 저장할 로그가 없습니다.",
                "chinese-simplified": "暂无可保存的日志。",
            },
            "logs_saved_to": {
                "english": "Logs saved to: {0}",
                "japanese": "ログを保存しました: {0}",
                "korean": "로그를 저장했습니다: {0}",
                "chinese-simplified": "日志已保存到：{0}",
            },
            "failed_to_save_logs": {
                "english": "Failed to save logs: {0}",
                "japanese": "ログを保存できませんでした: {0}",
                "korean": "로그를 저장하지 못했습니다: {0}",
                "chinese-simplified": "保存日志失败：{0}",
            },
            "select_item_to_preview": {
                "english": "Select an item in the list to preview it.",
                "japanese": "プレビューするには、リストから項目を選択してください。",
                "korean": "미리 보려면 목록에서 항목을 선택하세요.",
                "chinese-simplified": "请先在列表中选择要预览的项目。",
            },
            "preview_only_title": {
                "english": "Some Files Are Only Previews",
                "japanese": "一部のファイルはプレビューのみです",
                "korean": "일부 파일은 미리보기만 있습니다",
                "chinese-simplified": "部分文件只有预览图",
            },
            "preview_only_text": {
                "english": "{0} file(s) can't be downloaded because the site only has their preview images.",
                "japanese": "{0}件のファイルは、サイトにプレビュー画像しかないためダウンロードできません。",
                "korean": "{0}개의 파일은 사이트에 미리보기 이미지만 있어서 다운로드할 수 없습니다.",
                "chinese-simplified": "{0} 个文件无法下载，因为网站上只有它们的预览图。",
            },
            "preview_only_info": {
                "english": 'The site lists these files, but its media servers only kept their thumbnails, not the full files. This is not a problem with Kemono Downloader. These files are skipped and the other files download normally. To save the preview images instead, use the Thumbnail Downloader tab. Click "Show Details..." to see the list.',
                "japanese": "サイトにはこれらのファイルが掲載されていますが、メディアサーバーにはサムネイルしか残っておらず、元のファイルはありません。Kemono Downloaderの不具合ではありません。これらのファイルはスキップされ、他のファイルは通常どおりダウンロードされます。プレビュー画像を保存したい場合は、サムネイルダウンローダータブを使用してください。一覧は「Show Details...」をクリックすると表示されます。",
                "korean": '사이트에 이 파일들이 올라와 있지만 미디어 서버에는 원본 파일이 없고 썸네일만 남아 있습니다. Kemono Downloader의 문제가 아닙니다. 이 파일들은 건너뛰고 다른 파일은 정상적으로 다운로드됩니다. 미리보기 이미지를 저장하려면 썸네일 다운로더 탭을 사용하세요. 목록은 "Show Details..."를 클릭하면 볼 수 있습니다.',
                "chinese-simplified": "网站列出了这些文件，但其媒体服务器只保留了缩略图，没有完整文件。这不是 Kemono Downloader 的问题。这些文件会被跳过，其他文件照常下载。如需保存预览图，请使用“缩略图下载器”选项卡。点击“Show Details...”可查看列表。",
            },
            "preview_only_more": {
                "english": "... and {0} more",
                "japanese": "…ほか{0}件",
                "korean": "… 외 {0}개",
                "chinese-simplified": "……以及另外 {0} 个",
            },
            "preview_only_file_skipped": {
                "english": "Skipped {0}: the site only has a preview of this file",
                "japanese": "{0}をスキップしました：サイトにはこのファイルのプレビューしかありません",
                "korean": "{0} 건너뜀: 사이트에 이 파일의 미리보기만 있습니다",
                "chinese-simplified": "已跳过 {0}：网站上只有此文件的预览图",
            },
            "preview_only_skipped_log": {
                "english": "{0} file(s) are only available as previews on the site and were skipped (see the warning window for the list)",
                "japanese": "{0}件のファイルはサイト上でプレビューのみのため、スキップしました（一覧は警告ウィンドウを参照）",
                "korean": "{0}개의 파일은 사이트에 미리보기만 있어서 건너뛰었습니다(목록은 경고 창 참고)",
                "chinese-simplified": "{0} 个文件在网站上只有预览图，已跳过（列表见警告窗口）",
            },
            "preview_only_label": {
                "english": "preview only",
                "japanese": "プレビューのみ",
                "korean": "미리보기만",
                "chinese-simplified": "仅预览",
            },
            "preview_only_tooltip": {
                "english": "The site only has a preview of this file, so it can't be downloaded. Use the Thumbnail Downloader tab to save the preview.",
                "japanese": "サイトにはこのファイルのプレビューしかないため、ダウンロードできません。プレビューを保存するには、サムネイルダウンローダータブを使用してください。",
                "korean": "사이트에 이 파일의 미리보기만 있어서 다운로드할 수 없습니다. 미리보기를 저장하려면 썸네일 다운로더 탭을 사용하세요.",
                "chinese-simplified": "网站上只有此文件的预览图，因此无法下载。如需保存预览图，请使用“缩略图下载器”选项卡。",
            },
            "file_not_on_server": {
                "english": "Not available on the server (HTTP {0}): {1}. The site lists this file, but its media server doesn't have it, so it was skipped instead of retried. ({2})",
                "japanese": "サーバー上にありません（HTTP {0}）：{1}。サイトにはこのファイルが掲載されていますが、メディアサーバーにないため、再試行せずにスキップしました。（{2}）",
                "korean": "서버에 없음(HTTP {0}): {1}. 사이트에 이 파일이 올라와 있지만 미디어 서버에 없어서 재시도하지 않고 건너뛰었습니다. ({2})",
                "chinese-simplified": "服务器上没有此文件（HTTP {0}）：{1}。网站列出了此文件，但其媒体服务器上没有，因此已跳过，不再重试。（{2}）",
            },
            "files_not_on_server_count": {
                "english": "{0} file(s) were not available on the media server and were skipped",
                "japanese": "{0}件のファイルはメディアサーバー上になかったため、スキップしました",
                "korean": "{0}개의 파일은 미디어 서버에 없어서 건너뛰었습니다",
                "chinese-simplified": "{0} 个文件不在媒体服务器上，已跳过",
            },
            "download_summary": {
                "english": "Summary: {0} downloaded, {1} only available as previews (skipped), {2} not found on the server, {3} failed",
                "japanese": "概要：ダウンロード済み {0}件、プレビューのみ（スキップ）{1}件、サーバー上になし {2}件、失敗 {3}件",
                "korean": "요약: 다운로드 {0}개, 미리보기만 있음(건너뜀) {1}개, 서버에 없음 {2}개, 실패 {3}개",
                "chinese-simplified": "摘要：已下载 {0} 个，仅有预览图（已跳过）{1} 个，服务器上不存在 {2} 个，失败 {3} 个",
            },
            "save_preview_images": {
                "english": "Save the preview image when the site only has a preview of a file",
                "japanese": "サイトにプレビューしかないファイルは、プレビュー画像を保存する",
                "korean": "사이트에 미리보기만 있는 파일은 미리보기 이미지를 저장",
                "chinese-simplified": "网站上只有预览图的文件，保存其预览图",
            },
            "save_preview_images_tooltip": {
                "english": 'Some files are listed by the site but only their preview image remains. When this is on, that preview is downloaded next to the other files, named like "00501_preview.png". Only images have previews.',
                "japanese": "サイトに掲載されていても、プレビュー画像しか残っていないファイルがあります。オンにすると、そのプレビューを「00501_preview.png」のような名前で他のファイルと一緒にダウンロードします。プレビューがあるのは画像のみです。",
                "korean": '사이트에 올라와 있지만 미리보기 이미지만 남아 있는 파일이 있습니다. 켜면 그 미리보기를 "00501_preview.png" 같은 이름으로 다른 파일과 함께 다운로드합니다. 미리보기는 이미지에만 있습니다.',
                "chinese-simplified": "有些文件虽在网站上列出，但只剩下预览图。开启后，会将该预览图以“00501_preview.png”这样的名称，与其他文件一起下载。只有图片才有预览图。",
            },
            "preview_only_info_saved": {
                "english": 'The site lists these files, but its media servers only kept their thumbnails, not the full files. This is not a problem with Kemono Downloader. Their preview images are saved instead, named like "00501_preview.png", and the other files download normally. Click "Show Details..." to see the list.',
                "japanese": "サイトにはこれらのファイルが掲載されていますが、メディアサーバーにはサムネイルしか残っておらず、元のファイルはありません。Kemono Downloaderの不具合ではありません。代わりにプレビュー画像を「00501_preview.png」のような名前で保存し、他のファイルは通常どおりダウンロードします。一覧は「Show Details...」をクリックすると表示されます。",
                "korean": '사이트에 이 파일들이 올라와 있지만 미디어 서버에는 원본 파일이 없고 썸네일만 남아 있습니다. Kemono Downloader의 문제가 아닙니다. 대신 미리보기 이미지를 "00501_preview.png" 같은 이름으로 저장하고, 다른 파일은 정상적으로 다운로드합니다. 목록은 "Show Details..."를 클릭하면 볼 수 있습니다.',
                "chinese-simplified": "网站列出了这些文件，但其媒体服务器只保留了缩略图，没有完整文件。这不是 Kemono Downloader 的问题。将改为以“00501_preview.png”这样的名称保存其预览图，其他文件照常下载。点击“Show Details...”可查看列表。",
            },
            "preview_only_tooltip_saved": {
                "english": 'The site only has a preview of this file, so it can\'t be downloaded. Its preview image will be saved instead (the "save preview images" setting is on).',
                "japanese": "サイトにはこのファイルのプレビューしかないため、ダウンロードできません。代わりにプレビュー画像が保存されます（「プレビュー画像を保存」の設定がオンです）。",
                "korean": '사이트에 이 파일의 미리보기만 있어서 다운로드할 수 없습니다. 대신 미리보기 이미지가 저장됩니다("미리보기 이미지 저장" 설정이 켜져 있음).',
                "chinese-simplified": "网站上只有此文件的预览图，因此无法下载。将改为保存其预览图（“保存预览图”设置已开启）。",
            },
            "missing_files_title": {
                "english": "Some Files Aren't on the Server",
                "japanese": "サーバー上にないファイルがあります",
                "korean": "서버에 없는 파일이 있습니다",
                "chinese-simplified": "部分文件不在服务器上",
            },
            "missing_files_text": {
                "english": "{0} file(s) couldn't be downloaded because the site's media server doesn't have them.",
                "japanese": "{0}件のファイルは、サイトのメディアサーバーにないためダウンロードできませんでした。",
                "korean": "{0}개의 파일은 사이트의 미디어 서버에 없어서 다운로드할 수 없었습니다.",
                "chinese-simplified": "{0} 个文件无法下载，因为网站的媒体服务器上没有它们。",
            },
            "missing_files_info": {
                "english": "The site still lists these files, but its media server answered that they don't exist (HTTP 404). This is not a problem with Kemono Downloader, and trying again won't help. Click \"Show Details...\" to see the list.",
                "japanese": "サイトにはまだこれらのファイルが掲載されていますが、メディアサーバーは存在しないと応答しました（HTTP 404）。Kemono Downloaderの不具合ではなく、再試行しても解決しません。一覧は「Show Details...」をクリックすると表示されます。",
                "korean": '사이트에는 아직 이 파일들이 올라와 있지만, 미디어 서버는 파일이 없다고 응답했습니다(HTTP 404). Kemono Downloader의 문제가 아니며, 다시 시도해도 해결되지 않습니다. 목록은 "Show Details..."를 클릭하면 볼 수 있습니다.',
                "chinese-simplified": "网站仍列出这些文件，但其媒体服务器回应文件不存在（HTTP 404）。这不是 Kemono Downloader 的问题，重试也无济于事。点击“Show Details...”可查看列表。",
            },
            "history_files_tooltip": {
                "english": "{0} of {1} files downloaded.\n{2} only had a preview on the site (skipped).\n{3} weren't on the media server.",
                "japanese": "{1}件中{0}件のファイルをダウンロードしました。\n{2}件はサイトにプレビューしかありませんでした（スキップ）。\n{3}件はメディアサーバーにありませんでした。",
                "korean": "{1}개 중 {0}개 파일을 다운로드했습니다.\n{2}개는 사이트에 미리보기만 있었습니다(건너뜀).\n{3}개는 미디어 서버에 없었습니다.",
                "chinese-simplified": "已下载 {1} 个文件中的 {0} 个。\n{2} 个在网站上只有预览图（已跳过）。\n{3} 个不在媒体服务器上。",
            },
            # Help guide, section notes and the Browser Extension tab
            "note_folder_settings": {
                "english": "Everything is kept in Save Directory › Folder Name: your files in Downloads, preview images in Cache, and the history and the record of downloaded files in Other Files.",
                "japanese": "すべては「保存ディレクトリ › フォルダ名」に保存されます。ファイルは Downloads、プレビュー画像は Cache、履歴とダウンロード済みファイルの記録は Other Files に入ります。",
                "korean": "모든 데이터는 '저장 디렉토리 › 폴더 이름'에 보관됩니다. 파일은 Downloads, 미리보기 이미지는 Cache, 기록과 다운로드한 파일 목록은 Other Files에 저장됩니다.",
                "chinese-simplified": "所有内容都保存在“保存目录 › 文件夹名称”中：下载的文件在 Downloads，预览图在 Cache，历史记录和已下载文件的记录在 Other Files。",
            },
            "note_download_settings": {
                "english": "How many files download at the same time. More is faster but uses more bandwidth; Pawchive is always limited to five at a time; the info button explains why.",
                "japanese": "同時にダウンロードするファイル数です。多いほど速くなりますが、通信量も増えます。Pawchive は常に同時 5 件までに制限されます（理由は情報ボタンで確認できます）。",
                "korean": "동시에 다운로드할 파일 수입니다. 많을수록 빠르지만 대역폭을 더 사용합니다. Pawchive는 항상 동시에 5개로 제한됩니다(이유는 정보 버튼에서 확인하세요).",
                "chinese-simplified": "同时下载的文件数量。越多越快，但占用的带宽也越多；Pawchive 始终限制为同时 5 个（原因见信息按钮）。",
            },
            "note_retry_settings": {
                "english": "How many times the app tries again before giving up. Raise these on an unreliable connection; lower them to give up sooner.",
                "japanese": "あきらめる前に再試行する回数です。接続が不安定なときは増やし、早めにあきらめたいときは減らしてください。",
                "korean": "포기하기 전에 다시 시도하는 횟수입니다. 연결이 불안정하면 늘리고, 더 빨리 포기하려면 줄이세요.",
                "chinese-simplified": "放弃之前重试的次数。网络不稳定时可以调高，想更快放弃时可以调低。",
            },
            "note_creator_settings": {
                "english": "How files from the Creator tab are named and arranged. Press ? for the placeholders a template can use.",
                "japanese": "クリエイタータブでダウンロードしたファイルの名前と配置です。テンプレートで使えるプレースホルダーは ? で確認できます。",
                "korean": "크리에이터 탭에서 받은 파일의 이름과 배치 방식입니다. 템플릿에 쓸 수 있는 자리 표시자는 ? 버튼에서 확인하세요.",
                "chinese-simplified": "创作者选项卡下载的文件的命名和存放方式。按 ? 查看模板可用的占位符。",
            },
            "note_update_settings": {
                "english": "Checks GitHub for a newer version when the app starts and tells you about it. Nothing is installed automatically.",
                "japanese": "起動時に GitHub で新しいバージョンを確認し、あればお知らせします。自動でインストールされることはありません。",
                "korean": "앱을 시작할 때 GitHub에서 새 버전을 확인하고 알려 줍니다. 자동으로 설치되지는 않습니다.",
                "chinese-simplified": "启动时在 GitHub 上检查是否有新版本并通知你。不会自动安装任何内容。",
            },
            "note_language_settings": {
                "english": "The language of the whole app, including the Help guide. Applies after Apply Changes.",
                "japanese": "ヘルプのガイドを含む、アプリ全体の言語です。「変更を適用」の後に反映されます。",
                "korean": "도움말 안내를 포함한 앱 전체의 언어입니다. '변경 적용'을 누르면 반영됩니다.",
                "chinese-simplified": "整个应用（包括帮助指南）的语言。点击“应用更改”后生效。",
            },
            "note_font_settings": {
                "english": "The font for the whole app, logs included. Applies after Apply Changes.",
                "japanese": "ログを含む、アプリ全体のフォントです。「変更を適用」の後に反映されます。",
                "korean": "로그를 포함한 앱 전체의 글꼴입니다. '변경 적용'을 누르면 반영됩니다.",
                "chinese-simplified": "整个应用（包括日志）的字体。点击“应用更改”后生效。",
            },
            "note_post_queue": {
                "english": "Add post links here, one at a time or from a .txt file. Press the eye button on a post to list its files on the right.",
                "japanese": "投稿リンクを 1 件ずつ、または .txt ファイルから追加します。投稿の目のボタンを押すと、右側にファイルが一覧表示されます。",
                "korean": "게시물 링크를 하나씩 또는 .txt 파일에서 추가하세요. 게시물의 눈 버튼을 누르면 오른쪽에 파일 목록이 표시됩니다.",
                "chinese-simplified": "在这里逐个添加投稿链接，或从 .txt 文件导入。点击投稿上的眼睛按钮，右侧会列出其中的文件。",
            },
            "note_post_files": {
                "english": "Tick the files to download, or tick Download All Links to take every file of every queued post. Select an image and press the eye button to preview it.",
                "japanese": "ダウンロードするファイルにチェックを入れるか、「すべてのリンクをダウンロード」でキュー内のすべての投稿の全ファイルを取得します。画像を選んで目のボタンを押すとプレビューできます。",
                "korean": "다운로드할 파일을 선택하거나, '모든 링크 다운로드'로 대기열에 있는 모든 게시물의 파일을 받으세요. 이미지를 선택하고 눈 버튼을 누르면 미리 볼 수 있습니다.",
                "chinese-simplified": "勾选要下载的文件，或勾选“下载所有链接”下载队列中所有投稿的全部文件。选中图片后点击眼睛按钮即可预览。",
            },
            "note_creator_queue": {
                "english": "Add creator links here, one at a time or from a .txt file. Press the eye button on a creator to list their posts on the right.",
                "japanese": "クリエイターのリンクを 1 件ずつ、または .txt ファイルから追加します。クリエイターの目のボタンを押すと、右側に投稿が一覧表示されます。",
                "korean": "크리에이터 링크를 하나씩 또는 .txt 파일에서 추가하세요. 크리에이터의 눈 버튼을 누르면 오른쪽에 게시물 목록이 표시됩니다.",
                "chinese-simplified": "在这里逐个添加创作者链接，或从 .txt 文件导入。点击创作者上的眼睛按钮，右侧会列出其投稿。",
            },
            "note_creator_options": {
                "english": "Choose what to take from each post, then the file types below. Fast Mode downloads everything from many links with fewer clicks; its info button explains it.",
                "japanese": "各投稿から何を取得するかを選び、下でファイルの種類を選びます。高速モードでは、多くのリンクから少ない操作ですべてをダウンロードできます（詳しくは情報ボタンで）。",
                "korean": "각 게시물에서 무엇을 받을지 고른 다음, 아래에서 파일 형식을 고르세요. 빠른 모드는 여러 링크의 모든 것을 적은 클릭으로 다운로드합니다(자세한 내용은 정보 버튼).",
                "chinese-simplified": "选择要从每个投稿中获取的内容，再在下方选择文件类型。快速模式只需很少的操作，就能下载多个链接中的全部内容（详情见信息按钮）。",
            },
            "note_creator_posts": {
                "english": "Tick the posts to download. Check ALL (Page) ticks this page and Check ALL (All) every page; the arrows change page.",
                "japanese": "ダウンロードする投稿にチェックを入れます。「すべてチェック (ページ)」はこのページ、「すべてチェック (すべて)」は全ページが対象です。矢印でページを切り替えます。",
                "korean": "다운로드할 게시물을 선택하세요. '모두 선택 (페이지)'는 이 페이지, '모두 선택 (모두)'는 모든 페이지를 선택합니다. 화살표로 페이지를 넘깁니다.",
                "chinese-simplified": "勾选要下载的投稿。“全选 (页面)”勾选当前页，“全选 (全部)”勾选所有页；用箭头翻页。",
            },
            "note_thumb_mode": {
                "english": "Post takes post links; Creator takes creator links and finds the thumbnail of every post.",
                "japanese": "「投稿」は投稿リンク、「クリエイター」はクリエイターのリンクを受け付け、すべての投稿のサムネイルを探します。",
                "korean": "'포스트'는 게시물 링크를, '크리에이터'는 크리에이터 링크를 받아 모든 게시물의 썸네일을 찾습니다.",
                "chinese-simplified": "“帖子”使用投稿链接；“创作者”使用创作者链接，并查找其每个投稿的缩略图。",
            },
            "note_thumb_queue": {
                "english": "Add links, then press Detect Thumbnails to find the images to download.",
                "japanese": "リンクを追加してから「サムネイルを検出」を押すと、ダウンロードする画像が見つかります。",
                "korean": "링크를 추가한 뒤 '썸네일 감지'를 눌러 다운로드할 이미지를 찾으세요.",
                "chinese-simplified": "添加链接后点击“检测缩略图”，查找要下载的图片。",
            },
            "note_thumb_options": {
                "english": "Thumbnails are saved in Downloads/Thumbnails. Skip existing files leaves thumbnails you already have alone.",
                "japanese": "サムネイルは Downloads/Thumbnails に保存されます。「既存のファイルをスキップ」を使うと、既にあるサムネイルはそのままになります。",
                "korean": "썸네일은 Downloads/Thumbnails에 저장됩니다. '기존 파일 건너뛰기'를 켜면 이미 있는 썸네일은 그대로 둡니다.",
                "chinese-simplified": "缩略图保存在 Downloads/Thumbnails 中。勾选“跳过已存在的文件”后，已有的缩略图不会被覆盖。",
            },
            "note_thumb_list": {
                "english": "Tick the thumbnails to save; the filter narrows the list and the eye button previews the selected one.",
                "japanese": "保存するサムネイルにチェックを入れます。フィルターで一覧を絞り込み、目のボタンで選択中のサムネイルをプレビューできます。",
                "korean": "저장할 썸네일을 선택하세요. 필터로 목록을 좁히고, 눈 버튼으로 선택한 썸네일을 미리 볼 수 있습니다.",
                "chinese-simplified": "勾选要保存的缩略图；可用筛选框缩小列表，用眼睛按钮预览选中的缩略图。",
            },
            "note_history": {
                "english": "Every finished download and where it was saved. Removing records never deletes your files.",
                "japanese": "完了したすべてのダウンロードと保存先です。記録を削除しても、ファイルが削除されることはありません。",
                "korean": "완료된 모든 다운로드와 저장 위치입니다. 기록을 삭제해도 파일은 삭제되지 않습니다.",
                "chinese-simplified": "所有已完成的下载及其保存位置。删除记录绝不会删除你的文件。",
            },
            "note_favorites": {
                "english": "Links you saved with ★. Double-click a row to add its link to the queue, or double-click a title or note to edit it.",
                "japanese": "★ で保存したリンクです。行をダブルクリックするとキューに追加され、タイトルやメモをダブルクリックすると編集できます。",
                "korean": "★로 저장한 링크입니다. 행을 더블클릭하면 대기열에 추가되고, 제목이나 메모를 더블클릭하면 편집할 수 있습니다.",
                "chinese-simplified": "用 ★ 保存的链接。双击一行可将链接加入队列，双击标题或备注可进行编辑。",
            },
            "help_subtitle": {
                "english": "Pick a topic, or search the whole guide.",
                "japanese": "トピックを選ぶか、ガイド全体を検索してください。",
                "korean": "주제를 고르거나 안내서 전체를 검색하세요.",
                "chinese-simplified": "选择一个主题，或搜索整个指南。",
            },
            "help_search_placeholder": {
                "english": "Search the guide…",
                "japanese": "ガイドを検索…",
                "korean": "안내서 검색…",
                "chinese-simplified": "搜索指南…",
            },
            "help_previous": {
                "english": "Previous",
                "japanese": "前へ",
                "korean": "이전",
                "chinese-simplified": "上一页",
            },
            "help_next": {
                "english": "Next",
                "japanese": "次へ",
                "korean": "다음",
                "chinese-simplified": "下一页",
            },
            "help_no_results": {
                "english": "No topic matches your search.",
                "japanese": "検索に一致するトピックはありません。",
                "korean": "검색과 일치하는 주제가 없습니다.",
                "chinese-simplified": "没有与搜索内容匹配的主题。",
            },
            "guide_start_title": {
                "english": "Getting Started",
                "japanese": "はじめに",
                "korean": "시작하기",
                "chinese-simplified": "入门",
            },
            "guide_start_text": {
                "english": "<p>Kemono Downloader saves posts and whole creator archives from <b>Kemono</b>, <b>Coomer</b> and <b>Pawchive</b> to your computer.</p><h3>Quick start</h3><ol><li>Copy a post link (…/user/123/post/456) or a creator link (…/user/123) from the site.</li><li>Paste it into the <b>Post Downloader</b> or <b>Creator Downloader</b> tab and press <b>Add to Queue</b>.</li><li>Press the eye button on the queued link to list its files or posts, and tick what you want.</li><li>Press <b>Download</b>. Progress and messages appear in the console.</li></ol><h3>The tabs</h3><ul><li><b>Post Downloader</b>: files from individual posts.</li><li><b>Creator Downloader</b>: posts from one or more creators.</li><li><b>Thumbnail Downloader</b>: only the preview images of posts.</li><li><b>History</b>: finished downloads and your favorite links.</li><li><b>Settings</b>: folders, speed, retries, naming, language, font, proxy and Tor.</li><li><b>Help</b>: this guide.</li><li><b>Browser Extension</b>: a separate extension for downloading from your browser.</li></ul><h3>Where files go</h3><p>Everything is kept in one folder, set in Settings (Save Directory › Folder Name):</p><ul><li><b>Downloads</b>: your downloaded files (thumbnails go into Downloads/Thumbnails).</li><li><b>Cache</b>: temporary preview images.</li><li><b>Other Files</b>: the download history and the record of files already downloaded, so they are skipped next time.</li></ul>",
                "japanese": "<p>Kemono Downloader は、<b>Kemono</b>・<b>Coomer</b>・<b>Pawchive</b> の投稿やクリエイターのアーカイブ全体をパソコンに保存するアプリです。</p><h3>クイックスタート</h3><ol><li>サイトから投稿リンク（…/user/123/post/456）またはクリエイターのリンク（…/user/123）をコピーします。</li><li><b>投稿ダウンローダー</b>または<b>クリエイターダウンローダー</b>タブに貼り付け、<b>キューに追加</b>を押します。</li><li>キュー内のリンクの目のボタンを押してファイルや投稿を一覧表示し、必要なものにチェックを入れます。</li><li><b>ダウンロード</b>を押します。進行状況とメッセージはコンソールに表示されます。</li></ol><h3>タブ</h3><ul><li><b>投稿ダウンローダー</b>：個別の投稿のファイル。</li><li><b>クリエイターダウンローダー</b>：1 人以上のクリエイターの投稿。</li><li><b>サムネイルダウンローダー</b>：投稿のプレビュー画像だけ。</li><li><b>履歴</b>：完了したダウンロードとお気に入りのリンク。</li><li><b>設定</b>：フォルダ、速度、リトライ、名前の付け方、言語、フォント、プロキシと Tor。</li><li><b>ヘルプ</b>：このガイド。</li><li><b>ブラウザ拡張機能</b>：ブラウザからダウンロードするための別の拡張機能。</li></ul><h3>ファイルの保存先</h3><p>すべては設定で指定した 1 つのフォルダ（保存ディレクトリ › フォルダ名）に保存されます。</p><ul><li><b>Downloads</b>：ダウンロードしたファイル（サムネイルは Downloads/Thumbnails）。</li><li><b>Cache</b>：一時的なプレビュー画像。</li><li><b>Other Files</b>：ダウンロード履歴と、ダウンロード済みファイルの記録（次回はスキップされます）。</li></ul>",
                "korean": "<p>Kemono Downloader는 <b>Kemono</b>, <b>Coomer</b>, <b>Pawchive</b>의 게시물과 크리에이터 아카이브 전체를 컴퓨터에 저장하는 앱입니다.</p><h3>빠른 시작</h3><ol><li>사이트에서 게시물 링크(…/user/123/post/456)나 크리에이터 링크(…/user/123)를 복사합니다.</li><li><b>게시물 다운로더</b> 또는 <b>크리에이터 다운로더</b> 탭에 붙여 넣고 <b>대기열에 추가</b>를 누릅니다.</li><li>대기열에 있는 링크의 눈 버튼을 눌러 파일이나 게시물 목록을 보고, 원하는 항목을 선택합니다.</li><li><b>다운로드</b>를 누릅니다. 진행 상황과 메시지는 콘솔에 표시됩니다.</li></ol><h3>탭 안내</h3><ul><li><b>게시물 다운로더</b>: 개별 게시물의 파일.</li><li><b>크리에이터 다운로더</b>: 한 명 이상의 크리에이터의 게시물.</li><li><b>썸네일 다운로더</b>: 게시물의 미리보기 이미지만.</li><li><b>기록</b>: 완료된 다운로드와 즐겨찾기 링크.</li><li><b>설정</b>: 폴더, 속도, 재시도, 이름 규칙, 언어, 글꼴, 프록시와 Tor.</li><li><b>도움말</b>: 이 안내서.</li><li><b>브라우저 확장</b>: 브라우저에서 다운로드하기 위한 별도의 확장 프로그램.</li></ul><h3>파일 저장 위치</h3><p>모든 데이터는 설정에서 지정한 하나의 폴더(저장 디렉토리 › 폴더 이름)에 보관됩니다.</p><ul><li><b>Downloads</b>: 다운로드한 파일(썸네일은 Downloads/Thumbnails).</li><li><b>Cache</b>: 임시 미리보기 이미지.</li><li><b>Other Files</b>: 다운로드 기록과 이미 받은 파일 목록(다음에는 건너뜁니다).</li></ul>",
                "chinese-simplified": "<p>Kemono Downloader 可以把 <b>Kemono</b>、<b>Coomer</b> 和 <b>Pawchive</b> 上的投稿以及创作者的全部存档保存到你的电脑。</p><h3>快速开始</h3><ol><li>从网站复制投稿链接（…/user/123/post/456）或创作者链接（…/user/123）。</li><li>粘贴到<b>投稿下载器</b>或<b>创作者下载器</b>选项卡，然后点击<b>添加到队列</b>。</li><li>点击队列中链接的眼睛按钮，列出其中的文件或投稿，并勾选你需要的内容。</li><li>点击<b>下载</b>。进度和消息会显示在控制台中。</li></ol><h3>各个选项卡</h3><ul><li><b>投稿下载器</b>：单个投稿中的文件。</li><li><b>创作者下载器</b>：一个或多个创作者的投稿。</li><li><b>缩略图下载器</b>：只下载投稿的预览图。</li><li><b>历史记录</b>：已完成的下载和收藏的链接。</li><li><b>设置</b>：文件夹、速度、重试、命名、语言、字体、代理和 Tor。</li><li><b>帮助</b>：本指南。</li><li><b>浏览器扩展</b>：一个独立的浏览器扩展，用于在浏览器中下载。</li></ul><h3>文件保存位置</h3><p>所有内容都保存在设置中指定的一个文件夹里（保存目录 › 文件夹名称）：</p><ul><li><b>Downloads</b>：下载的文件（缩略图在 Downloads/Thumbnails 中）。</li><li><b>Cache</b>：临时预览图。</li><li><b>Other Files</b>：下载历史和已下载文件的记录（下次会跳过这些文件）。</li></ul>",
            },
            "guide_post_title": {
                "english": "Post Downloader",
                "japanese": "投稿ダウンローダー",
                "korean": "게시물 다운로더",
                "chinese-simplified": "投稿下载器",
            },
            "guide_post_text": {
                "english": "<p>Downloads the files of individual posts.</p><h3>Add posts</h3><ul><li>Paste a post link and press <b>Add to Queue</b>, or import many from a .txt file with one link per line.</li><li>The ★ button saves the link to Favorites in the History tab.</li><li>Press the eye button on a queued post to list its files under <b>Files to Download</b>; the ✕ button removes it from the queue.</li></ul><h3>Choose files</h3><ul><li>Tick the files you want. <b>Filter by Type</b> and the search box narrow the list, and <b>Check ALL (Page)</b> ticks everything shown.</li><li><b>Download All Links</b> downloads every file of every queued post without picking files.</li><li>Select an image and press the eye button under the list to preview it.</li><li>Files marked <b>preview only</b> no longer have a full copy on the site and can't be downloaded (see Logs and Reports).</li></ul><h3>Options</h3><ul><li><b>Fast Mode</b>: paste many links at once and download everything from them with fewer clicks; finished links leave the queue automatically. Its info button explains it.</li><li><b>Auto Rename and sort File name by order</b>: puts each file's position in the post in front of its name, such as <i>1_cover.png</i>, so files sort in post order.</li><li><b>Download Post Text</b>: also saves the post's text as <i>desc.txt</i>.</li></ul><h3>Download</h3><p>Press <b>Download</b>. The two bars show the current file and the overall progress; <b>Cancel</b> stops, and <b>Expand Logs</b> opens the full log. Files are saved in <i>Downloads/&lt;service&gt;/&lt;post ID&gt;_&lt;post title&gt;</i>, and files you already downloaded are skipped.</p>",
                "japanese": "<p>個別の投稿のファイルをダウンロードします。</p><h3>投稿を追加する</h3><ul><li>投稿リンクを貼り付けて<b>キューに追加</b>を押すか、1 行に 1 リンクの .txt ファイルからまとめて読み込みます。</li><li>★ ボタンはリンクを履歴タブのお気に入りに保存します。</li><li>キュー内の投稿の目のボタンを押すと<b>ダウンロードするファイル</b>に一覧表示され、✕ ボタンでキューから削除できます。</li></ul><h3>ファイルを選ぶ</h3><ul><li>必要なファイルにチェックを入れます。<b>タイプでフィルタリング</b>と検索ボックスで一覧を絞り込み、<b>すべてチェック (ページ)</b>で表示中のものをすべて選べます。</li><li><b>すべてのリンクをダウンロード</b>は、ファイルを選ばずにキュー内のすべての投稿の全ファイルをダウンロードします。</li><li>画像を選んで一覧の下の目のボタンを押すとプレビューできます。</li><li><b>プレビューのみ</b>と表示されたファイルは、サイト上に完全なファイルが残っておらず、ダウンロードできません（「ログとレポート」を参照）。</li></ul><h3>オプション</h3><ul><li><b>高速モード</b>：多数のリンクをまとめて貼り付け、少ない操作ですべてをダウンロードします。完了したリンクは自動でキューから外れます。詳しくは情報ボタンを参照してください。</li><li><b>自動リネームとファイル名を順序で並べ替え</b>：投稿内での順番をファイル名の先頭に付け（例：<i>1_cover.png</i>）、投稿の順に並ぶようにします。</li><li><b>投稿テキストをダウンロード</b>：投稿の本文も <i>desc.txt</i> として保存します。</li></ul><h3>ダウンロード</h3><p><b>ダウンロード</b>を押します。2 本のバーは現在のファイルと全体の進行状況を示します。<b>キャンセル</b>で停止し、<b>ログを展開</b>で全ログを開けます。ファイルは <i>Downloads/&lt;サービス&gt;/&lt;投稿ID&gt;_&lt;投稿タイトル&gt;</i> に保存され、ダウンロード済みのファイルはスキップされます。</p>",
                "korean": "<p>개별 게시물의 파일을 다운로드합니다.</p><h3>게시물 추가</h3><ul><li>게시물 링크를 붙여 넣고 <b>대기열에 추가</b>를 누르거나, 한 줄에 링크 하나씩 적힌 .txt 파일에서 한꺼번에 가져오세요.</li><li>★ 버튼은 링크를 기록 탭의 즐겨찾기에 저장합니다.</li><li>대기열에 있는 게시물의 눈 버튼을 누르면 <b>다운로드할 파일</b>에 목록이 표시되고, ✕ 버튼은 대기열에서 삭제합니다.</li></ul><h3>파일 선택</h3><ul><li>원하는 파일을 선택하세요. <b>유형별 필터링</b>과 검색 상자로 목록을 좁히고, <b>모두 선택 (페이지)</b>로 표시된 항목을 모두 선택할 수 있습니다.</li><li><b>모든 링크 다운로드</b>는 파일을 고르지 않고 대기열에 있는 모든 게시물의 파일을 전부 다운로드합니다.</li><li>이미지를 선택하고 목록 아래의 눈 버튼을 누르면 미리 볼 수 있습니다.</li><li><b>미리보기만</b>으로 표시된 파일은 사이트에 원본이 남아 있지 않아 다운로드할 수 없습니다('로그와 보고서' 참고).</li></ul><h3>옵션</h3><ul><li><b>빠른 모드</b>: 여러 링크를 한꺼번에 붙여 넣고 적은 클릭으로 모두 다운로드합니다. 완료된 링크는 대기열에서 자동으로 빠집니다. 자세한 내용은 정보 버튼을 보세요.</li><li><b>자동 이름 바꾸기 및 순서별 파일 이름 정렬</b>: 게시물 안에서의 순서를 파일 이름 앞에 붙여(예: <i>1_cover.png</i>) 게시물 순서대로 정렬되게 합니다.</li><li><b>게시물 텍스트 다운로드</b>: 게시물 본문도 <i>desc.txt</i>로 저장합니다.</li></ul><h3>다운로드</h3><p><b>다운로드</b>를 누르세요. 두 막대는 현재 파일과 전체 진행 상황을 보여 줍니다. <b>취소</b>로 멈추고, <b>로그 확장</b>으로 전체 로그를 엽니다. 파일은 <i>Downloads/&lt;서비스&gt;/&lt;게시물 ID&gt;_&lt;게시물 제목&gt;</i>에 저장되며, 이미 받은 파일은 건너뜁니다.</p>",
                "chinese-simplified": "<p>下载单个投稿中的文件。</p><h3>添加投稿</h3><ul><li>粘贴投稿链接并点击<b>添加到队列</b>，或从每行一个链接的 .txt 文件中批量导入。</li><li>★ 按钮会把链接保存到历史记录选项卡的收藏夹中。</li><li>点击队列中投稿的眼睛按钮，其文件会列在<b>将要下载的文件</b>中；✕ 按钮会将其从队列中移除。</li></ul><h3>选择文件</h3><ul><li>勾选需要的文件。<b>按类型过滤</b>和搜索框可以缩小列表，<b>全选 (页面)</b>会勾选当前显示的所有文件。</li><li><b>下载所有链接</b>无需挑选，直接下载队列中所有投稿的全部文件。</li><li>选中图片后点击列表下方的眼睛按钮即可预览。</li><li>标为<b>仅预览</b>的文件在网站上已没有完整副本，无法下载（参见“日志和报告”）。</li></ul><h3>选项</h3><ul><li><b>快速模式</b>：一次粘贴多个链接，只需很少的操作即可全部下载；完成的链接会自动移出队列。详情请看信息按钮。</li><li><b>自动重命名并按顺序排序文件名</b>：在文件名前加上它在投稿中的序号（例如 <i>1_cover.png</i>），让文件按投稿顺序排列。</li><li><b>下载帖子文本</b>：同时把投稿正文保存为 <i>desc.txt</i>。</li></ul><h3>下载</h3><p>点击<b>下载</b>。两个进度条分别显示当前文件和整体进度；<b>取消</b>可停止，<b>展开日志</b>可打开完整日志。文件保存在 <i>Downloads/&lt;服务&gt;/&lt;投稿 ID&gt;_&lt;投稿标题&gt;</i> 中，已下载过的文件会被跳过。</p>",
            },
            "guide_creator_title": {
                "english": "Creator Downloader",
                "japanese": "クリエイターダウンローダー",
                "korean": "크리에이터 다운로더",
                "chinese-simplified": "创作者下载器",
            },
            "guide_creator_text": {
                "english": "<p>Downloads posts from one or more creators.</p><h3>Add creators</h3><ul><li>Paste a creator link (…/service/user/ID) and press <b>Add to Queue</b>, or import a .txt file with one link per line. ★ saves the link to Favorites.</li><li>Press the eye button on a queued creator to list their posts under <b>Posts to Download</b>.</li></ul><h3>Choose posts</h3><ul><li>Tick posts, or use <b>Check ALL (Page)</b> for the page shown and <b>Check ALL (All)</b> for every page. The arrows change page and the search box filters by title.</li><li>Select a post and press the eye button under the list to preview its thumbnail.</li></ul><h3>Choose content</h3><ul><li><b>Main File</b>, <b>Attachments</b> and <b>Content Images</b> (images inside the post text) choose what is taken from each post.</li><li><b>File Extensions</b> limits the download to the ticked file types.</li><li><b>Fast Mode</b>, <b>Auto Rename</b> and <b>Download Post Text</b> work as in the Post Downloader.</li></ul><h3>Names and folders</h3><p>File names and the folder layout come from <b>Settings › Creator Downloader</b>: one folder per post (the default), all files in the creator folder, or subfolders by file type.</p>",
                "japanese": "<p>1 人以上のクリエイターの投稿をダウンロードします。</p><h3>クリエイターを追加する</h3><ul><li>クリエイターのリンク（…/サービス/user/ID）を貼り付けて<b>キューに追加</b>を押すか、1 行に 1 リンクの .txt ファイルを読み込みます。★ でリンクをお気に入りに保存できます。</li><li>キュー内のクリエイターの目のボタンを押すと、<b>ダウンロードする投稿</b>に投稿が一覧表示されます。</li></ul><h3>投稿を選ぶ</h3><ul><li>投稿にチェックを入れるか、表示中のページには<b>すべてチェック (ページ)</b>、全ページには<b>すべてチェック (すべて)</b>を使います。矢印でページを切り替え、検索ボックスでタイトルを絞り込めます。</li><li>投稿を選んで一覧の下の目のボタンを押すと、サムネイルをプレビューできます。</li></ul><h3>取得する内容を選ぶ</h3><ul><li><b>メインファイル</b>、<b>添付ファイル</b>、<b>コンテンツ画像</b>（本文中の画像）で、各投稿から何を取得するかを選びます。</li><li><b>ファイル拡張子</b>で、チェックした種類のファイルだけをダウンロードします。</li><li><b>高速モード</b>、<b>自動リネーム</b>、<b>投稿テキストをダウンロード</b>は投稿ダウンローダーと同じです。</li></ul><h3>名前とフォルダ</h3><p>ファイル名とフォルダ構成は<b>設定 › クリエイターダウンローダー</b>で決まります。投稿ごとのフォルダ（デフォルト）、クリエイターフォルダにすべて保存、ファイルタイプ別のサブフォルダから選べます。</p>",
                "korean": "<p>한 명 이상의 크리에이터 게시물을 다운로드합니다.</p><h3>크리에이터 추가</h3><ul><li>크리에이터 링크(…/서비스/user/ID)를 붙여 넣고 <b>대기열에 추가</b>를 누르거나, 한 줄에 링크 하나씩 적힌 .txt 파일을 가져오세요. ★는 링크를 즐겨찾기에 저장합니다.</li><li>대기열에 있는 크리에이터의 눈 버튼을 누르면 <b>다운로드할 게시물</b>에 게시물 목록이 표시됩니다.</li></ul><h3>게시물 선택</h3><ul><li>게시물을 선택하거나, 현재 페이지는 <b>모두 선택 (페이지)</b>, 모든 페이지는 <b>모두 선택 (모두)</b>를 사용하세요. 화살표로 페이지를 넘기고, 검색 상자로 제목을 걸러 냅니다.</li><li>게시물을 선택하고 목록 아래의 눈 버튼을 누르면 썸네일을 미리 볼 수 있습니다.</li></ul><h3>받을 내용 선택</h3><ul><li><b>메인 파일</b>, <b>첨부 파일</b>, <b>콘텐츠 이미지</b>(본문 안의 이미지)로 각 게시물에서 무엇을 받을지 고릅니다.</li><li><b>파일 확장자</b>에서 선택한 형식의 파일만 다운로드합니다.</li><li><b>빠른 모드</b>, <b>자동 이름 바꾸기</b>, <b>게시물 텍스트 다운로드</b>는 게시물 다운로더와 같습니다.</li></ul><h3>이름과 폴더</h3><p>파일 이름과 폴더 구조는 <b>설정 › 크리에이터 다운로더</b>에서 정합니다. 게시물별 폴더(기본), 크리에이터 폴더에 모두 저장, 파일 유형별 하위 폴더 중에서 고를 수 있습니다.</p>",
                "chinese-simplified": "<p>下载一个或多个创作者的投稿。</p><h3>添加创作者</h3><ul><li>粘贴创作者链接（…/服务/user/ID）并点击<b>添加到队列</b>，或导入每行一个链接的 .txt 文件。★ 可以把链接保存到收藏夹。</li><li>点击队列中创作者的眼睛按钮，其投稿会列在<b>将要下载的投稿</b>中。</li></ul><h3>选择投稿</h3><ul><li>勾选投稿，或用<b>全选 (页面)</b>勾选当前页、用<b>全选 (全部)</b>勾选所有页。箭头用于翻页，搜索框可按标题筛选。</li><li>选中一个投稿并点击列表下方的眼睛按钮，可预览其缩略图。</li></ul><h3>选择内容</h3><ul><li><b>主要文件</b>、<b>附件</b>和<b>内容图片</b>（正文中的图片）决定从每个投稿中获取哪些内容。</li><li><b>文件扩展名</b>把下载范围限制为已勾选的文件类型。</li><li><b>快速模式</b>、<b>自动重命名</b>和<b>下载帖子文本</b>的作用与投稿下载器相同。</li></ul><h3>名称和文件夹</h3><p>文件名和文件夹结构由<b>设置 › 创作者下载器</b>决定：按帖子创建文件夹（默认）、全部保存在创作者文件夹中，或按文件类型创建子文件夹。</p>",
            },
            "guide_thumbnails_title": {
                "english": "Thumbnail Downloader",
                "japanese": "サムネイルダウンローダー",
                "korean": "썸네일 다운로더",
                "chinese-simplified": "缩略图下载器",
            },
            "guide_thumbnails_text": {
                "english": "<p>Saves only the preview images (thumbnails) of posts, which is much faster than downloading the files.</p><ul><li>Choose <b>Post</b> or <b>Creator</b> as the download mode, then add links of that kind, or import a .txt file. Switching mode asks before clearing the queue.</li><li>Press <b>Detect Thumbnails</b> to find them, then tick the ones to save. The filter box narrows the list and the eye button previews the selected one.</li><li>Options: how many download at once (1–10), <b>Skip existing files</b>, <b>Auto Rename</b> and <b>Download Post Text</b>.</li><li>Press <b>Start Download</b>. Thumbnails are saved in <i>Downloads/Thumbnails</i>, and the log console on the right shows what happens.</li></ul>",
                "japanese": "<p>投稿のプレビュー画像（サムネイル）だけを保存します。ファイルをダウンロードするよりずっと速く終わります。</p><ul><li>ダウンロードモードで<b>投稿</b>か<b>クリエイター</b>を選び、その種類のリンクを追加するか .txt ファイルを読み込みます。モードを切り替えると、キューを消去する前に確認されます。</li><li><b>サムネイルを検出</b>を押して探し、保存するものにチェックを入れます。フィルターで一覧を絞り込み、目のボタンで選択中のものをプレビューできます。</li><li>オプション：同時ダウンロード数（1〜10）、<b>既存のファイルをスキップ</b>、<b>自動リネーム</b>、<b>投稿テキストをダウンロード</b>。</li><li><b>ダウンロード開始</b>を押します。サムネイルは <i>Downloads/Thumbnails</i> に保存され、右側のログコンソールに経過が表示されます。</li></ul>",
                "korean": "<p>게시물의 미리보기 이미지(썸네일)만 저장합니다. 파일을 다운로드하는 것보다 훨씬 빠릅니다.</p><ul><li>다운로드 모드에서 <b>포스트</b> 또는 <b>크리에이터</b>를 고른 뒤, 그 종류의 링크를 추가하거나 .txt 파일을 가져오세요. 모드를 바꾸면 대기열을 지우기 전에 확인합니다.</li><li><b>썸네일 감지</b>를 눌러 찾은 다음, 저장할 항목을 선택하세요. 필터로 목록을 좁히고, 눈 버튼으로 선택한 항목을 미리 볼 수 있습니다.</li><li>옵션: 동시 다운로드 수(1~10), <b>기존 파일 건너뛰기</b>, <b>자동 이름 바꾸기</b>, <b>게시물 텍스트 다운로드</b>.</li><li><b>다운로드 시작</b>을 누르세요. 썸네일은 <i>Downloads/Thumbnails</i>에 저장되고, 오른쪽 로그 콘솔에 진행 상황이 표시됩니다.</li></ul>",
                "chinese-simplified": "<p>只保存投稿的预览图（缩略图），比下载文件快得多。</p><ul><li>选择<b>帖子</b>或<b>创作者</b>下载模式，然后添加对应类型的链接，或导入 .txt 文件。切换模式时，会在清空队列前询问你。</li><li>点击<b>检测缩略图</b>进行查找，然后勾选要保存的缩略图。筛选框可以缩小列表，眼睛按钮可以预览选中的缩略图。</li><li>选项：同时下载数量（1–10）、<b>跳过已存在的文件</b>、<b>自动重命名</b>和<b>下载帖子文本</b>。</li><li>点击<b>开始下载</b>。缩略图保存在 <i>Downloads/Thumbnails</i> 中，右侧的日志控制台会显示过程。</li></ul>",
            },
            "guide_history_title": {
                "english": "History and Favorites",
                "japanese": "履歴とお気に入り",
                "korean": "기록과 즐겨찾기",
                "chinese-simplified": "历史记录和收藏夹",
            },
            "guide_history_text": {
                "english": "<h3>Download History</h3><ul><li>Every finished post, creator and thumbnail download is listed with its date, type, files (done/total and failures), posts, size on disk, duration and status. Hover the files column for how many were preview-only or missing from the server.</li><li>Search by title, link or creator and filter by type; the line above the table adds up what is shown.</li><li><b>Open Folder</b> (or a double-click) opens where the files were saved. If the folder was moved or deleted, the app offers to locate it, open the nearest parent folder, or download it again.</li><li><b>Copy Link</b>, <b>Add to Queue</b> and <b>Add to Favorites</b> work on several rows at once. <b>Remove</b> and <b>Clear History</b> delete only the records, never your files.</li><li>Untick <b>Record download history</b> to stop recording; <b>Export CSV</b> saves the list for a spreadsheet.</li></ul><h3>Favorites</h3><ul><li>Save links with ★ in the Post or Creator tab, from the history, or by pasting a link into the Favorites view.</li><li>Double-click a title or note to edit it; double-click elsewhere on a row to add the link to the queue.</li><li>Copy links, open them in your browser, or import and export them as a .txt file with one link per line.</li></ul>",
                "japanese": "<h3>ダウンロード履歴</h3><ul><li>完了した投稿・クリエイター・サムネイルのダウンロードが、日時、種類、ファイル数（完了/合計と失敗）、投稿数、ディスク上のサイズ、所要時間、状態とともに一覧表示されます。ファイル列にカーソルを合わせると、プレビューのみやサーバーになかったファイルの数が表示されます。</li><li>タイトル・リンク・クリエイターで検索し、種類で絞り込めます。表の上の行に表示中の合計が出ます。</li><li><b>フォルダーを開く</b>（またはダブルクリック）で保存先を開きます。フォルダーが移動・削除されていた場合は、場所の指定、最も近い親フォルダーを開く、再ダウンロードのいずれかを選べます。</li><li><b>リンクをコピー</b>、<b>キューに追加</b>、<b>お気に入りに追加</b>は複数の行にまとめて使えます。<b>削除</b>と<b>履歴を消去</b>は記録だけを消し、ファイルは削除しません。</li><li><b>ダウンロード履歴を記録</b>のチェックを外すと記録を止めます。<b>CSVにエクスポート</b>で一覧を表計算ソフト用に保存できます。</li></ul><h3>お気に入り</h3><ul><li>投稿・クリエイタータブの ★、履歴、またはお気に入り画面にリンクを貼り付けて保存します。</li><li>タイトルやメモをダブルクリックすると編集でき、行のそれ以外の場所をダブルクリックするとリンクがキューに追加されます。</li><li>リンクのコピー、ブラウザで開く、1 行に 1 リンクの .txt ファイルとしてのインポートとエクスポートができます。</li></ul>",
                "korean": "<h3>다운로드 기록</h3><ul><li>완료된 게시물·크리에이터·썸네일 다운로드가 날짜, 유형, 파일 수(완료/전체와 실패), 게시물 수, 디스크 크기, 소요 시간, 상태와 함께 표시됩니다. 파일 열에 마우스를 올리면 미리보기만 있었거나 서버에 없던 파일 수를 볼 수 있습니다.</li><li>제목·링크·크리에이터로 검색하고 유형으로 걸러 낼 수 있습니다. 표 위의 줄에 표시된 항목의 합계가 나옵니다.</li><li><b>폴더 열기</b>(또는 더블클릭)로 저장 위치를 엽니다. 폴더가 이동되거나 삭제되었으면 위치 찾기, 가장 가까운 상위 폴더 열기, 다시 다운로드 중에서 고를 수 있습니다.</li><li><b>링크 복사</b>, <b>대기열에 추가</b>, <b>즐겨찾기에 추가</b>는 여러 행에 한꺼번에 쓸 수 있습니다. <b>삭제</b>와 <b>기록 지우기</b>는 기록만 지우고 파일은 지우지 않습니다.</li><li><b>다운로드 기록 저장</b>을 해제하면 기록을 멈춥니다. <b>CSV로 내보내기</b>로 목록을 스프레드시트용으로 저장합니다.</li></ul><h3>즐겨찾기</h3><ul><li>게시물·크리에이터 탭의 ★, 기록, 또는 즐겨찾기 화면에 링크를 붙여 넣어 저장합니다.</li><li>제목이나 메모를 더블클릭하면 편집하고, 행의 다른 곳을 더블클릭하면 링크가 대기열에 추가됩니다.</li><li>링크를 복사하거나, 브라우저에서 열거나, 한 줄에 링크 하나씩 적힌 .txt 파일로 가져오고 내보낼 수 있습니다.</li></ul>",
                "chinese-simplified": "<h3>下载历史</h3><ul><li>所有已完成的投稿、创作者和缩略图下载都会列出，包括日期、类型、文件数（完成/总数及失败数）、投稿数、磁盘大小、耗时和状态。把鼠标悬停在文件列上，可以看到仅预览和服务器上缺失的文件数量。</li><li>可按标题、链接或创作者搜索，并按类型筛选；表格上方一行会汇总当前显示的内容。</li><li><b>打开文件夹</b>（或双击）会打开文件的保存位置。如果文件夹已被移动或删除，应用会让你选择定位文件夹、打开最近的上级文件夹或重新下载。</li><li><b>复制链接</b>、<b>添加到队列</b>和<b>添加到收藏夹</b>可以同时作用于多行。<b>删除</b>和<b>清除历史</b>只删除记录，绝不删除你的文件。</li><li>取消勾选<b>记录下载历史</b>即可停止记录；<b>导出 CSV</b> 可把列表保存为表格文件。</li></ul><h3>收藏夹</h3><ul><li>可通过投稿或创作者选项卡中的 ★、历史记录，或把链接粘贴到收藏夹视图来保存链接。</li><li>双击标题或备注可以编辑；双击行的其他位置会把链接加入队列。</li><li>可以复制链接、在浏览器中打开，或以每行一个链接的 .txt 文件导入和导出。</li></ul>",
            },
            "guide_settings_title": {
                "english": "Settings",
                "japanese": "設定",
                "korean": "설정",
                "chinese-simplified": "设置",
            },
            "guide_settings_text": {
                "english": "<p>Change settings, then press <b>Apply Changes</b> and confirm. <b>Reset to Defaults</b> fills in the default values, which also need Apply Changes. The Use Proxy switch and proxy type are saved straight away.</p><ul><li><b>Folder Settings</b>: where everything is kept (Save Directory › Folder Name). <b>Open Directory</b> opens it.</li><li><b>Download Settings</b>: how many files download at once (1–20, default 5). Pawchive is always limited to five at a time; the info button next to it explains why. The preview image option saves the preview of files the site only has a preview of, named like <i>00501_preview.png</i>.</li><li><b>Retry Settings</b>: how many times to try before giving up. <b>Creator Posts Max Attempts</b> covers loading a creator's post list (read 50 posts at a time), <b>Post Data Max Retries</b> a post's details, <b>File Download Max Retries</b> each file, and <b>API Request Max Retries</b> link checks and other site requests.</li><li><b>Creator Downloader</b>: the file name template, from a preset or your own (press <b>?</b> for placeholders such as {post_title} and {file_index}), and the folder layout.</li><li><b>Update Settings</b>: check GitHub for a new version at startup. The app tells you and links to the release; nothing is installed for you.</li><li><b>Language</b> and <b>Font</b>: apply to the whole app, logs included.</li><li><b>Proxy Settings</b>: see Proxy and Tor.</li></ul>",
                "japanese": "<p>設定を変更したら<b>変更を適用</b>を押して確認します。<b>デフォルトにリセット</b>は初期値を入力するだけなので、反映するには「変更を適用」も押してください。「プロキシを使用」とプロキシの種類はすぐに保存されます。</p><ul><li><b>フォルダ設定</b>：すべての保存先（保存ディレクトリ › フォルダ名）。<b>ディレクトリを開く</b>で開けます。</li><li><b>ダウンロード設定</b>：同時にダウンロードするファイル数（1〜20、デフォルト 5）。Pawchive は常に同時 5 件までに制限されます（理由は横の情報ボタンで確認できます）。プレビュー画像のオプションを使うと、サイトにプレビューしかないファイルのプレビューを <i>00501_preview.png</i> のような名前で保存します。</li><li><b>リトライ設定</b>：あきらめる前に試す回数です。<b>クリエイター投稿最大試行回数</b>はクリエイターの投稿一覧の読み込み（50 件ずつ）、<b>投稿データ最大リトライ回数</b>は投稿の詳細、<b>ファイルダウンロード最大リトライ回数</b>は各ファイル、<b>APIリクエスト最大リトライ回数</b>はリンクの確認などサイトへのその他のリクエストが対象です。</li><li><b>クリエイターダウンローダー</b>：ファイル名テンプレート（プリセットまたは独自のもの。{post_title} や {file_index} などのプレースホルダーは <b>?</b> で確認）とフォルダ構造。</li><li><b>更新設定</b>：起動時に GitHub で新しいバージョンを確認します。お知らせとリリースへのリンクを表示するだけで、自動でインストールはしません。</li><li><b>言語</b>と<b>フォント</b>：ログを含むアプリ全体に適用されます。</li><li><b>プロキシ設定</b>：「プロキシと Tor」を参照してください。</li></ul>",
                "korean": "<p>설정을 바꾼 뒤 <b>변경 적용</b>을 누르고 확인하세요. <b>기본값으로 재설정</b>은 기본값을 채워 넣을 뿐이므로, 반영하려면 '변경 적용'도 누르세요. '프록시 사용'과 프록시 종류는 바로 저장됩니다.</p><ul><li><b>폴더 설정</b>: 모든 데이터를 보관하는 위치(저장 디렉토리 › 폴더 이름). <b>디렉토리 열기</b>로 열 수 있습니다.</li><li><b>다운로드 설정</b>: 동시에 다운로드할 파일 수(1~20, 기본 5). Pawchive는 항상 동시에 5개로 제한됩니다(이유는 옆의 정보 버튼에서 확인). 미리보기 이미지 옵션을 켜면 사이트에 미리보기만 있는 파일의 미리보기를 <i>00501_preview.png</i> 같은 이름으로 저장합니다.</li><li><b>재시도 설정</b>: 포기하기 전에 시도하는 횟수입니다. <b>크리에이터 게시물 최대 시도 횟수</b>는 크리에이터의 게시물 목록 불러오기(한 번에 50개), <b>게시물 데이터 최대 재시도 횟수</b>는 게시물 상세 정보, <b>파일 다운로드 최대 재시도 횟수</b>는 각 파일, <b>API 요청 최대 재시도 횟수</b>는 링크 확인 등 사이트에 대한 기타 요청에 적용됩니다.</li><li><b>크리에이터 다운로더</b>: 파일 이름 템플릿(미리 정의된 것 또는 직접 입력. {post_title}, {file_index} 같은 자리 표시자는 <b>?</b>에서 확인)과 폴더 구조.</li><li><b>업데이트 설정</b>: 시작할 때 GitHub에서 새 버전을 확인합니다. 알림과 릴리스 링크만 보여 주며, 자동으로 설치하지는 않습니다.</li><li><b>언어</b>와 <b>글꼴</b>: 로그를 포함한 앱 전체에 적용됩니다.</li><li><b>프록시 설정</b>: '프록시와 Tor'를 보세요.</li></ul>",
                "chinese-simplified": "<p>修改设置后，点击<b>应用更改</b>并确认。<b>重置为默认值</b>只会填入默认值，仍需点击“应用更改”才会生效。“使用代理”开关和代理类型会立即保存。</p><ul><li><b>文件夹设置</b>：所有内容的保存位置（保存目录 › 文件夹名称）。<b>打开目录</b>可打开它。</li><li><b>下载设置</b>：同时下载的文件数量（1–20，默认 5）。Pawchive 始终限制为同时 5 个，原因见旁边的信息按钮。开启预览图选项后，网站上只有预览图的文件会以 <i>00501_preview.png</i> 这样的名称保存其预览图。</li><li><b>重试设置</b>：放弃之前尝试的次数。<b>创作者帖子最大尝试次数</b>用于加载创作者的投稿列表（每次 50 个），<b>帖子数据最大重试次数</b>用于投稿详情，<b>文件下载最大重试次数</b>用于每个文件，<b>API请求最大重试次数</b>用于链接检查和其他网站请求。</li><li><b>创作者下载器</b>：文件名模板（可选预设或自己输入，按 <b>?</b> 查看 {post_title}、{file_index} 等占位符）和文件夹结构。</li><li><b>更新设置</b>：启动时在 GitHub 上检查新版本。应用只会通知你并提供发布页面链接，不会替你安装任何内容。</li><li><b>语言</b>和<b>字体</b>：应用于整个应用，包括日志。</li><li><b>代理设置</b>：参见“代理和 Tor”。</li></ul>",
            },
            "guide_proxy_title": {
                "english": "Proxy and Tor",
                "japanese": "プロキシと Tor",
                "korean": "프록시와 Tor",
                "chinese-simplified": "代理和 Tor",
            },
            "guide_proxy_text": {
                "english": "<p>Tick <b>Use Proxy</b> in Settings to send downloads through a proxy. The choice is saved straight away.</p><h3>Custom proxy</h3><ul><li>Enter the address as <i>host:port</i>, <i>http://host:port</i> or <i>socks5h://host:port</i>, adding <i>user:password@</i> before the host if the proxy needs a login.</li><li><b>Test Proxy</b> checks that it works.</li></ul><h3>Tor</h3><ol><li>Press <b>Download Tor</b>. The app downloads the official Tor Expert Bundle and checks it against Tor's published checksum before using it. Or press <b>Browse</b> to use a Tor program you already have.</li><li>Press <b>Start Tor</b> and wait until the status reads <i>Running</i>.</li><li>Press <b>Test Tor</b> to check the connection.</li></ol><p>Downloads always go through Tor's port (9050), so a Tor service you run yourself works too. If Tor isn't running, downloads fail instead of using your own connection, so your IP address is never used by accident.</p>",
                "japanese": "<p>設定で<b>プロキシを使用</b>にチェックを入れると、ダウンロードがプロキシを経由します。この選択はすぐに保存されます。</p><h3>カスタムプロキシ</h3><ul><li>アドレスを <i>host:port</i>、<i>http://host:port</i>、<i>socks5h://host:port</i> の形式で入力します。ログインが必要な場合は、ホストの前に <i>user:password@</i> を付けます。</li><li><b>プロキシをテスト</b>で動作を確認できます。</li></ul><h3>Tor</h3><ol><li><b>Torをダウンロード</b>を押します。アプリは公式の Tor Expert Bundle をダウンロードし、使う前に Tor が公開しているチェックサムと照合します。手持ちの Tor を使う場合は<b>参照</b>を押します。</li><li><b>Torを開始</b>を押し、状態が<i>実行中</i>になるまで待ちます。</li><li><b>Torをテスト</b>で接続を確認します。</li></ol><p>ダウンロードは常に Tor のポート（9050）を経由するため、自分で実行している Tor サービスも使えます。Tor が動いていない場合、ダウンロードは自分の接続を使わずに失敗するので、IP アドレスが誤って使われることはありません。</p>",
                "korean": "<p>설정에서 <b>프록시 사용</b>을 선택하면 다운로드가 프록시를 거칩니다. 이 선택은 바로 저장됩니다.</p><h3>사용자 지정 프록시</h3><ul><li>주소를 <i>host:port</i>, <i>http://host:port</i>, <i>socks5h://host:port</i> 형식으로 입력하세요. 로그인이 필요하면 호스트 앞에 <i>user:password@</i>를 붙입니다.</li><li><b>프록시 테스트</b>로 작동하는지 확인합니다.</li></ul><h3>Tor</h3><ol><li><b>Tor 다운로드</b>를 누르세요. 앱이 공식 Tor Expert Bundle을 받아, 사용하기 전에 Tor가 공개한 체크섬과 대조합니다. 이미 있는 Tor 프로그램을 쓰려면 <b>찾아보기</b>를 누르세요.</li><li><b>Tor 시작</b>을 누르고 상태가 <i>실행 중</i>이 될 때까지 기다리세요.</li><li><b>Tor 테스트</b>로 연결을 확인합니다.</li></ol><p>다운로드는 항상 Tor의 포트(9050)를 거치므로, 직접 실행 중인 Tor 서비스도 사용할 수 있습니다. Tor가 실행 중이 아니면 내 연결을 쓰지 않고 다운로드가 실패하므로, IP 주소가 실수로 노출되지 않습니다.</p>",
                "chinese-simplified": "<p>在设置中勾选<b>使用代理</b>后，下载会通过代理进行。这个选择会立即保存。</p><h3>自定义代理</h3><ul><li>按 <i>host:port</i>、<i>http://host:port</i> 或 <i>socks5h://host:port</i> 格式输入地址；如果代理需要登录，请在主机前加上 <i>user:password@</i>。</li><li><b>测试代理</b>可检查代理是否可用。</li></ul><h3>Tor</h3><ol><li>点击<b>下载Tor</b>。应用会下载官方的 Tor Expert Bundle，并在使用前与 Tor 公布的校验和进行核对。若要使用你已有的 Tor 程序，请点击<b>浏览</b>。</li><li>点击<b>启动Tor</b>，等待状态变为<i>运行中</i>。</li><li>点击<b>测试Tor</b>检查连接。</li></ol><p>下载始终通过 Tor 的端口（9050）进行，因此你自己运行的 Tor 服务也可以使用。如果 Tor 未运行，下载会失败，而不会使用你自己的网络连接，因此你的 IP 地址不会被意外暴露。</p>",
            },
            "guide_logs_title": {
                "english": "Logs and Reports",
                "japanese": "ログとレポート",
                "korean": "로그와 보고서",
                "chinese-simplified": "日志和报告",
            },
            "guide_logs_text": {
                "english": "<ul><li>The console in each downloader tab shows what is happening: green for progress, yellow for warnings and red for errors.</li><li><b>Expand Logs</b> opens the full log. It keeps your place while new lines arrive (<b>Jump to Latest</b> returns to the newest), and you can search it (Ctrl+F; Enter for the next match, Shift+Enter for the previous), copy everything, save it as a .txt file, or clear it.</li><li>Each download ends with a summary of how many files were downloaded, were only previews, were not on the server, or failed.</li><li><b>Preview only</b>: the site lists the file, but only its preview image remains, so it is skipped. A window lists these files, and Settings can save their previews instead.</li><li><b>Not on the media server</b>: the site lists the file, but its server answers that the file doesn't exist (HTTP 404). Retrying doesn't help and it isn't a problem with the app. A window lists these files.</li><li>If something unexpected goes wrong, a window shows details to include in a bug report, and the app keeps running.</li></ul>",
                "japanese": "<ul><li>各ダウンローダータブのコンソールに経過が表示されます。緑は進行状況、黄色は警告、赤はエラーです。</li><li><b>ログを展開</b>で全ログを開きます。新しい行が届いても読んでいる位置を保ち（<b>最新へ移動</b>で最新に戻れます）、検索（Ctrl+F、Enter で次、Shift+Enter で前）、すべてコピー、.txt ファイルへの保存、クリアができます。</li><li>ダウンロードの終わりに、ダウンロードできた数、プレビューのみだった数、サーバーになかった数、失敗した数のまとめが表示されます。</li><li><b>プレビューのみ</b>：サイトにはファイルが掲載されていますが、プレビュー画像しか残っていないためスキップされます。該当ファイルはウィンドウに一覧表示され、設定でプレビューを代わりに保存することもできます。</li><li><b>メディアサーバーにない</b>：サイトにはファイルが掲載されていますが、サーバーがファイルは存在しないと応答します（HTTP 404）。再試行しても解決せず、アプリの問題でもありません。該当ファイルはウィンドウに一覧表示されます。</li><li>予期しない問題が起きた場合は、バグ報告に含める詳細がウィンドウに表示され、アプリはそのまま動き続けます。</li></ul>",
                "korean": "<ul><li>각 다운로더 탭의 콘솔에 진행 상황이 표시됩니다. 초록색은 진행, 노란색은 경고, 빨간색은 오류입니다.</li><li><b>로그 확장</b>은 전체 로그를 엽니다. 새 줄이 들어와도 읽던 위치를 유지하고(<b>최신으로 이동</b>으로 최신 줄로 돌아감), 검색(Ctrl+F, Enter는 다음, Shift+Enter는 이전), 모두 복사, .txt 파일로 저장, 지우기를 할 수 있습니다.</li><li>다운로드가 끝나면 받은 파일, 미리보기만 있던 파일, 서버에 없던 파일, 실패한 파일의 수를 요약해 보여 줍니다.</li><li><b>미리보기만</b>: 사이트에 파일이 올라와 있지만 미리보기 이미지만 남아 있어 건너뜁니다. 해당 파일은 창에 표시되며, 설정에서 대신 미리보기를 저장하게 할 수 있습니다.</li><li><b>미디어 서버에 없음</b>: 사이트에 파일이 올라와 있지만 서버가 파일이 없다고 응답합니다(HTTP 404). 다시 시도해도 해결되지 않으며 앱의 문제도 아닙니다. 해당 파일은 창에 표시됩니다.</li><li>예상치 못한 문제가 생기면 버그 보고에 넣을 세부 정보가 창에 표시되고, 앱은 계속 실행됩니다.</li></ul>",
                "chinese-simplified": "<ul><li>每个下载器选项卡的控制台会显示正在发生的事情：绿色表示进度，黄色表示警告，红色表示错误。</li><li><b>展开日志</b>会打开完整日志。新日志到来时会保持你正在阅读的位置（<b>跳到最新</b>可回到最新一行），还可以搜索（Ctrl+F；Enter 查找下一个，Shift+Enter 查找上一个）、全部复制、保存为 .txt 文件或清除。</li><li>每次下载结束时会显示汇总：已下载、仅有预览、服务器上没有以及失败的文件数量。</li><li><b>仅预览</b>：网站列出了该文件，但只剩下预览图，因此会被跳过。窗口会列出这些文件，你也可以在设置中改为保存它们的预览图。</li><li><b>不在媒体服务器上</b>：网站列出了该文件，但其服务器回应文件不存在（HTTP 404）。重试也无济于事，这也不是应用的问题。窗口会列出这些文件。</li><li>如果发生意外问题，窗口会显示可附在错误报告中的详细信息，应用会继续运行。</li></ul>",
            },
            "guide_troubleshooting_title": {
                "english": "Troubleshooting",
                "japanese": "トラブルシューティング",
                "korean": "문제 해결",
                "chinese-simplified": "故障排除",
            },
            "guide_troubleshooting_text": {
                "english": "<h3>Connection errors or nothing downloads</h3><p>Check your internet connection and that the site opens in your browser; sites are sometimes down for a while. If you use a proxy or Tor, test it in Settings or turn the proxy off.</p><h3>No files or posts appear</h3><p>Make sure the link suits the tab: a post link (…/user/ID/post/ID) for the Post Downloader, a creator link (…/user/ID) for the Creator Downloader. Press the eye button on the queued link, and tick files or posts (or Download All Links) before pressing Download.</p><h3>Files are skipped or reported missing</h3><p>Files marked preview only, and files the media server reports as not found (HTTP 404), can't be downloaded from the site. See Logs and Reports.</p><h3>Downloads are slow</h3><p>Try a different Simultaneous Downloads value in Settings. Pawchive is limited on purpose to five downloads at a time and one new file request per second. Tor is slower than a direct connection.</p><h3>Tor doesn't work</h3><p>Use Download Tor (or Browse to your Tor program), press Start Tor, wait for Running, then press Test Tor. Tor Output shows Tor's own messages if it can't connect.</p><h3>A setting didn't change</h3><p>Most settings, including language and font, take effect only after Apply Changes and its confirmation.</p><h3>Where are my files?</h3><p>Open Directory in Settings › Folder Settings opens the main folder, and Open Folder in the History tab opens the folder of a finished download.</p>",
                "japanese": "<h3>接続エラーが出る、何もダウンロードされない</h3><p>インターネット接続と、ブラウザでサイトが開けるかを確認してください。サイトが一時的に停止していることがあります。プロキシや Tor を使っている場合は、設定でテストするか、プロキシをオフにしてください。</p><h3>ファイルや投稿が表示されない</h3><p>タブに合ったリンクか確認してください。投稿ダウンローダーには投稿リンク（…/user/ID/post/ID）、クリエイターダウンローダーにはクリエイターのリンク（…/user/ID）を使います。キュー内のリンクの目のボタンを押し、ダウンロードの前にファイルや投稿にチェックを入れて（または「すべてのリンクをダウンロード」を使って）ください。</p><h3>ファイルがスキップされる、見つからないと表示される</h3><p>プレビューのみのファイルと、メディアサーバーが見つからないと応答したファイル（HTTP 404）は、サイトからダウンロードできません。「ログとレポート」を参照してください。</p><h3>ダウンロードが遅い</h3><p>設定の同時ダウンロード数を変えてみてください。Pawchive は意図的に、同時 5 件まで、新しいファイルの要求は 1 秒に 1 回までに制限されています。Tor は直接接続より遅くなります。</p><h3>Tor が使えない</h3><p>「Torをダウンロード」を使う（または「参照」で Tor のプログラムを選ぶ）、「Torを開始」を押して「実行中」になるのを待ち、「Torをテスト」を押してください。接続できない場合は、Tor出力に Tor 自身のメッセージが表示されます。</p><h3>設定が変わらない</h3><p>言語やフォントを含むほとんどの設定は、「変更を適用」を押して確認した後に反映されます。</p><h3>ファイルはどこ？</h3><p>設定 › フォルダ設定の「ディレクトリを開く」でメインフォルダを、履歴タブの「フォルダーを開く」で完了したダウンロードのフォルダを開けます。</p>",
                "korean": "<h3>연결 오류가 나거나 아무것도 다운로드되지 않음</h3><p>인터넷 연결과 브라우저에서 사이트가 열리는지 확인하세요. 사이트가 잠시 중단될 때가 있습니다. 프록시나 Tor를 쓰고 있다면 설정에서 테스트하거나 프록시를 끄세요.</p><h3>파일이나 게시물이 표시되지 않음</h3><p>탭에 맞는 링크인지 확인하세요. 게시물 다운로더에는 게시물 링크(…/user/ID/post/ID), 크리에이터 다운로더에는 크리에이터 링크(…/user/ID)를 씁니다. 대기열에 있는 링크의 눈 버튼을 누르고, 다운로드하기 전에 파일이나 게시물을 선택하세요(또는 '모든 링크 다운로드' 사용).</p><h3>파일을 건너뛰거나 없다고 표시됨</h3><p>미리보기만 있는 파일과 미디어 서버가 찾을 수 없다고 응답한 파일(HTTP 404)은 사이트에서 다운로드할 수 없습니다. '로그와 보고서'를 보세요.</p><h3>다운로드가 느림</h3><p>설정에서 동시 다운로드 값을 바꿔 보세요. Pawchive는 일부러 동시에 5개, 새 파일 요청은 1초에 한 번으로 제한됩니다. Tor는 직접 연결보다 느립니다.</p><h3>Tor가 작동하지 않음</h3><p>'Tor 다운로드'를 쓰거나 '찾아보기'로 Tor 프로그램을 고른 뒤, 'Tor 시작'을 누르고 '실행 중'이 되면 'Tor 테스트'를 누르세요. 연결되지 않으면 Tor 출력에 Tor 자체 메시지가 표시됩니다.</p><h3>설정이 바뀌지 않음</h3><p>언어와 글꼴을 포함한 대부분의 설정은 '변경 적용'을 누르고 확인한 뒤에 반영됩니다.</p><h3>파일은 어디에 있나요?</h3><p>설정 › 폴더 설정의 '디렉토리 열기'는 메인 폴더를, 기록 탭의 '폴더 열기'는 완료된 다운로드의 폴더를 엽니다.</p>",
                "chinese-simplified": "<h3>出现连接错误或没有任何下载</h3><p>请检查网络连接，并确认网站能在浏览器中打开；网站有时会暂时无法访问。如果使用了代理或 Tor，请在设置中测试，或关闭代理。</p><h3>没有显示文件或投稿</h3><p>请确认链接与选项卡相符：投稿下载器使用投稿链接（…/user/ID/post/ID），创作者下载器使用创作者链接（…/user/ID）。点击队列中链接的眼睛按钮，并在下载前勾选文件或投稿（或使用“下载所有链接”）。</p><h3>文件被跳过或显示缺失</h3><p>标为仅预览的文件，以及媒体服务器回应找不到的文件（HTTP 404），都无法从网站下载。参见“日志和报告”。</p><h3>下载很慢</h3><p>在设置中尝试调整并行下载数。Pawchive 被有意限制为同时 5 个下载、每秒最多发起一个新的文件请求。Tor 比直接连接慢。</p><h3>Tor 无法使用</h3><p>使用“下载Tor”（或点击“浏览”选择你的 Tor 程序），点击“启动Tor”，等待状态变为“运行中”，然后点击“测试Tor”。如果无法连接，Tor输出中会显示 Tor 自己的消息。</p><h3>设置没有改变</h3><p>包括语言和字体在内的大多数设置，需要点击“应用更改”并确认后才会生效。</p><h3>我的文件在哪里？</h3><p>设置 › 文件夹设置中的“打开目录”会打开主文件夹，历史记录选项卡中的“打开文件夹”会打开已完成下载的文件夹。</p>",
            },
            "guide_support_title": {
                "english": "Support and Updates",
                "japanese": "サポートと更新",
                "korean": "지원과 업데이트",
                "chinese-simplified": "支持与更新",
            },
            "guide_support_text": {
                "english": "<ul><li>Report bugs or suggest features on GitHub: <a href='https://github.com/VoxDroid/KemonoDownloader/issues'>github.com/VoxDroid/KemonoDownloader/issues</a>. Say what you did and what happened, and attach the log (Expand Logs › Download Logs).</li><li>Please report security problems privately through the repository's Security tab rather than in a public issue.</li><li>With Auto Check for Updates on, the app tells you when a new version is out. All releases are at <a href='https://github.com/VoxDroid/KemonoDownloader/releases'>GitHub Releases</a>.</li><li>Kemono Downloader is free, open-source software by VoxDroid, released under the MIT license.</li></ul>",
                "japanese": "<ul><li>バグの報告や機能の提案は GitHub へ：<a href='https://github.com/VoxDroid/KemonoDownloader/issues'>github.com/VoxDroid/KemonoDownloader/issues</a>。行った操作と起きたことを書き、ログ（ログを展開 › ログをダウンロード）を添付してください。</li><li>セキュリティ上の問題は、公開の issue ではなく、リポジトリの Security タブから非公開で報告してください。</li><li>自動更新チェックがオンなら、新しいバージョンが出たときにお知らせします。すべてのリリースは <a href='https://github.com/VoxDroid/KemonoDownloader/releases'>GitHub Releases</a> にあります。</li><li>Kemono Downloader は VoxDroid による無料のオープンソースソフトウェアで、MIT ライセンスで公開されています。</li></ul>",
                "korean": "<ul><li>버그 신고나 기능 제안은 GitHub에서 해 주세요: <a href='https://github.com/VoxDroid/KemonoDownloader/issues'>github.com/VoxDroid/KemonoDownloader/issues</a>. 무엇을 했고 어떤 일이 일어났는지 적고, 로그(로그 확장 › 로그 다운로드)를 첨부하세요.</li><li>보안 문제는 공개 이슈 대신 저장소의 Security 탭을 통해 비공개로 알려 주세요.</li><li>자동 업데이트 확인을 켜 두면 새 버전이 나왔을 때 알려 줍니다. 모든 릴리스는 <a href='https://github.com/VoxDroid/KemonoDownloader/releases'>GitHub Releases</a>에 있습니다.</li><li>Kemono Downloader는 VoxDroid가 만든 무료 오픈 소스 소프트웨어이며 MIT 라이선스로 배포됩니다.</li></ul>",
                "chinese-simplified": "<ul><li>在 GitHub 上报告错误或提出功能建议：<a href='https://github.com/VoxDroid/KemonoDownloader/issues'>github.com/VoxDroid/KemonoDownloader/issues</a>。请说明你做了什么、发生了什么，并附上日志（展开日志 › 下载日志）。</li><li>安全问题请通过仓库的 Security 选项卡私下报告，不要发布在公开的 issue 中。</li><li>开启自动检查更新后，有新版本时应用会通知你。所有版本都在 <a href='https://github.com/VoxDroid/KemonoDownloader/releases'>GitHub Releases</a> 上。</li><li>Kemono Downloader 是由 VoxDroid 开发的免费开源软件，采用 MIT 许可证发布。</li></ul>",
            },
            "ext_subtitle": {
                "english": "A separate extension that adds download controls to Kemono and Coomer post pages. It works without the desktop app and saves files through your browser's downloads.",
                "japanese": "Kemono と Coomer の投稿ページにダウンロード機能を追加する、別の拡張機能です。デスクトップアプリなしで動作し、ブラウザのダウンロード機能でファイルを保存します。",
                "korean": "Kemono와 Coomer 게시물 페이지에 다운로드 기능을 추가하는 별도의 확장 프로그램입니다. 데스크톱 앱 없이 작동하며, 브라우저의 다운로드 기능으로 파일을 저장합니다.",
                "chinese-simplified": "一个独立的扩展，会在 Kemono 和 Coomer 的投稿页面上添加下载功能。它无需桌面应用即可使用，并通过浏览器的下载功能保存文件。",
            },
            "ext_feature_pick_title": {
                "english": "Pick files",
                "japanese": "ファイルを選ぶ",
                "korean": "파일 선택",
                "chinese-simplified": "挑选文件",
            },
            "ext_feature_pick_text": {
                "english": "Choose a post's files with checkboxes.",
                "japanese": "投稿のファイルをチェックボックスで選べます。",
                "korean": "체크박스로 게시물의 파일을 고릅니다.",
                "chinese-simplified": "用复选框选择投稿中的文件。",
            },
            "ext_feature_zip_title": {
                "english": "ZIP or separate",
                "japanese": "ZIP または個別",
                "korean": "ZIP 또는 개별",
                "chinese-simplified": "ZIP 或单独下载",
            },
            "ext_feature_zip_text": {
                "english": "Get several files as one ZIP, or each on its own, which suits large videos.",
                "japanese": "複数のファイルを 1 つの ZIP にまとめるか、1 つずつ保存できます（大きな動画向き）。",
                "korean": "여러 파일을 ZIP 하나로 받거나 하나씩 받을 수 있습니다(큰 동영상에 적합).",
                "chinese-simplified": "可以把多个文件打包成一个 ZIP，也可以逐个下载（适合大型视频）。",
            },
            "ext_feature_progress_title": {
                "english": "Progress",
                "japanese": "進行状況",
                "korean": "진행 상황",
                "chinese-simplified": "进度",
            },
            "ext_feature_progress_text": {
                "english": "Follow each download while it runs.",
                "japanese": "ダウンロード中の進行状況を確認できます。",
                "korean": "다운로드 진행 상황을 실시간으로 볼 수 있습니다.",
                "chinese-simplified": "实时查看每个下载的进度。",
            },
            "ext_feature_sites_title": {
                "english": "Kemono and Coomer",
                "japanese": "Kemono と Coomer",
                "korean": "Kemono와 Coomer",
                "chinese-simplified": "Kemono 和 Coomer",
            },
            "ext_feature_sites_text": {
                "english": "Works on kemono.cr and coomer.st post pages.",
                "japanese": "kemono.cr と coomer.st の投稿ページで動作します。",
                "korean": "kemono.cr와 coomer.st 게시물 페이지에서 작동합니다.",
                "chinese-simplified": "适用于 kemono.cr 和 coomer.st 的投稿页面。",
            },
            "ext_install_heading": {
                "english": "Install it",
                "japanese": "インストール方法",
                "korean": "설치 방법",
                "chinese-simplified": "安装方法",
            },
            "ext_step_get_title": {
                "english": "1. Get the extension",
                "japanese": "1. 拡張機能を入手する",
                "korean": "1. 확장 프로그램 받기",
                "chinese-simplified": "1. 获取扩展",
            },
            "ext_step_get_text": {
                "english": "On the release page, download <b>Source code (zip)</b> and unzip it. The extension is the <b>browser-extension</b> folder inside. You can also browse that folder on GitHub.",
                "japanese": "リリースページで <b>Source code (zip)</b> をダウンロードして展開します。拡張機能は中の <b>browser-extension</b> フォルダです。GitHub でこのフォルダを見ることもできます。",
                "korean": "릴리스 페이지에서 <b>Source code (zip)</b>를 받아 압축을 푸세요. 확장 프로그램은 그 안의 <b>browser-extension</b> 폴더입니다. GitHub에서 이 폴더를 볼 수도 있습니다.",
                "chinese-simplified": "在发布页面下载 <b>Source code (zip)</b> 并解压。扩展就是其中的 <b>browser-extension</b> 文件夹。你也可以在 GitHub 上查看这个文件夹。",
            },
            "ext_step_manifest_title": {
                "english": "2. Choose your browser's manifest",
                "japanese": "2. ブラウザ用のマニフェストを選ぶ",
                "korean": "2. 브라우저용 매니페스트 고르기",
                "chinese-simplified": "2. 选择对应浏览器的清单文件",
            },
            "ext_step_manifest_text": {
                "english": "The folder has one manifest per browser. Copy the right one over <b>manifest.json</b>; the manifest.json there by default is only a placeholder and won't load.<br>• Chrome, Edge and other Chromium browsers: <b>chrome_manifest.json</b><br>• Firefox: <b>firefox_manifest.json</b>",
                "japanese": "フォルダにはブラウザごとのマニフェストがあります。正しいものを <b>manifest.json</b> に上書きコピーしてください。最初からある manifest.json は仮のもので、読み込めません。<br>• Chrome、Edge などの Chromium 系ブラウザ：<b>chrome_manifest.json</b><br>• Firefox：<b>firefox_manifest.json</b>",
                "korean": "폴더에는 브라우저별 매니페스트가 있습니다. 알맞은 파일을 <b>manifest.json</b>에 덮어 복사하세요. 기본으로 들어 있는 manifest.json은 임시 파일이라 로드되지 않습니다.<br>• Chrome, Edge 등 Chromium 브라우저: <b>chrome_manifest.json</b><br>• Firefox: <b>firefox_manifest.json</b>",
                "chinese-simplified": "文件夹中为每种浏览器准备了一个清单文件。请把对应的文件复制并覆盖 <b>manifest.json</b>；默认的 manifest.json 只是占位文件，无法加载。<br>• Chrome、Edge 等 Chromium 浏览器：<b>chrome_manifest.json</b><br>• Firefox：<b>firefox_manifest.json</b>",
            },
            "ext_commands_label": {
                "english": "Or run one of these in the browser-extension folder:",
                "japanese": "または browser-extension フォルダで次のいずれかを実行します：",
                "korean": "또는 browser-extension 폴더에서 다음 중 하나를 실행하세요:",
                "chinese-simplified": "或在 browser-extension 文件夹中运行以下命令之一：",
            },
            "ext_step_chrome_title": {
                "english": "3. Load it in Chrome or Edge",
                "japanese": "3. Chrome または Edge で読み込む",
                "korean": "3. Chrome 또는 Edge에서 로드",
                "chinese-simplified": "3. 在 Chrome 或 Edge 中加载",
            },
            "ext_step_chrome_text": {
                "english": "Open <b>chrome://extensions</b> (or <b>edge://extensions</b>), turn on <b>Developer mode</b>, press <b>Load unpacked</b> and choose the browser-extension folder.",
                "japanese": "<b>chrome://extensions</b>（または <b>edge://extensions</b>）を開き、<b>デベロッパー モード</b>をオンにして<b>パッケージ化されていない拡張機能を読み込む</b>を押し、browser-extension フォルダを選びます。",
                "korean": "<b>chrome://extensions</b>(또는 <b>edge://extensions</b>)를 열고 <b>개발자 모드</b>를 켠 다음 <b>압축해제된 확장 프로그램을 로드합니다</b>를 눌러 browser-extension 폴더를 고르세요.",
                "chinese-simplified": "打开 <b>chrome://extensions</b>（或 <b>edge://extensions</b>），开启<b>开发者模式</b>，点击<b>加载已解压的扩展程序</b>，然后选择 browser-extension 文件夹。",
            },
            "ext_step_firefox_title": {
                "english": "3. Load it in Firefox",
                "japanese": "3. Firefox で読み込む",
                "korean": "3. Firefox에서 로드",
                "chinese-simplified": "3. 在 Firefox 中加载",
            },
            "ext_step_firefox_text": {
                "english": "Open <b>about:debugging#/runtime/this-firefox</b>, press <b>Load Temporary Add-on…</b> and choose the folder's manifest.json. Firefox removes temporary add-ons when it restarts, so load it again after a restart.",
                "japanese": "<b>about:debugging#/runtime/this-firefox</b> を開き、<b>一時的なアドオンを読み込む…</b>を押してフォルダ内の manifest.json を選びます。Firefox は再起動すると一時的なアドオンを削除するので、再起動後はもう一度読み込んでください。",
                "korean": "<b>about:debugging#/runtime/this-firefox</b>를 열고 <b>임시 부가 기능 로드…</b>를 눌러 폴더의 manifest.json을 고르세요. Firefox는 다시 시작하면 임시 부가 기능을 제거하므로, 재시작 후에는 다시 로드해야 합니다.",
                "chinese-simplified": "打开 <b>about:debugging#/runtime/this-firefox</b>，点击<b>临时载入附加组件…</b>，然后选择文件夹中的 manifest.json。Firefox 重启时会移除临时附加组件，所以重启后需要重新加载。",
            },
            "ext_use_title": {
                "english": "Using it",
                "japanese": "使い方",
                "korean": "사용 방법",
                "chinese-simplified": "使用方法",
            },
            "ext_use_text": {
                "english": "Open a post on kemono.cr or coomer.st. The extension adds its download controls to the page: tick the files, choose a ZIP or separate files, and download. Files go to your browser's download folder.",
                "japanese": "kemono.cr または coomer.st で投稿を開きます。拡張機能がページにダウンロード機能を追加するので、ファイルにチェックを入れ、ZIP か個別かを選んでダウンロードします。ファイルはブラウザのダウンロードフォルダに保存されます。",
                "korean": "kemono.cr나 coomer.st에서 게시물을 여세요. 확장 프로그램이 페이지에 다운로드 기능을 추가합니다. 파일을 선택하고 ZIP 또는 개별 파일을 고른 뒤 다운로드하세요. 파일은 브라우저의 다운로드 폴더에 저장됩니다.",
                "chinese-simplified": "在 kemono.cr 或 coomer.st 上打开一个投稿。扩展会在页面上添加下载功能：勾选文件，选择 ZIP 或单独文件，然后下载。文件会保存到浏览器的下载文件夹。",
            },
            "ext_trouble_title": {
                "english": "If something doesn't work",
                "japanese": "うまくいかないとき",
                "korean": "문제가 있을 때",
                "chinese-simplified": "遇到问题时",
            },
            "ext_trouble_text": {
                "english": "<ul><li><b>No download controls</b>: make sure you're on a post page (…/post/…) of kemono.cr or coomer.st, then reload the page.</li><li><b>Manifest or service worker errors when loading</b>: the placeholder manifest.json was loaded. Copy your browser's manifest over it (step 2) and load the folder again.</li><li><b>The extension disappeared in Firefox</b>: temporary add-ons are removed on restart; load it again.</li><li><b>Downloads blocked</b>: if your browser asks, allow the site to download multiple files.</li></ul>",
                "japanese": "<ul><li><b>ダウンロード機能が表示されない</b>：kemono.cr または coomer.st の投稿ページ（…/post/…）にいることを確認し、ページを再読み込みしてください。</li><li><b>読み込み時にマニフェストや service worker のエラーが出る</b>：仮の manifest.json が読み込まれています。ブラウザ用のマニフェストを上書きコピー（手順 2）してから、もう一度フォルダを読み込んでください。</li><li><b>Firefox で拡張機能が消えた</b>：一時的なアドオンは再起動で削除されます。もう一度読み込んでください。</li><li><b>ダウンロードがブロックされる</b>：ブラウザに聞かれたら、そのサイトに複数ファイルのダウンロードを許可してください。</li></ul>",
                "korean": "<ul><li><b>다운로드 기능이 보이지 않음</b>: kemono.cr나 coomer.st의 게시물 페이지(…/post/…)인지 확인하고 페이지를 새로고침하세요.</li><li><b>로드할 때 매니페스트나 service worker 오류</b>: 임시 manifest.json이 로드된 것입니다. 브라우저용 매니페스트를 덮어 복사(2단계)한 뒤 폴더를 다시 로드하세요.</li><li><b>Firefox에서 확장 프로그램이 사라짐</b>: 임시 부가 기능은 재시작하면 제거됩니다. 다시 로드하세요.</li><li><b>다운로드가 차단됨</b>: 브라우저가 물어보면 해당 사이트의 여러 파일 다운로드를 허용하세요.</li></ul>",
                "chinese-simplified": "<ul><li><b>没有出现下载功能</b>：请确认你在 kemono.cr 或 coomer.st 的投稿页面（…/post/…）上，然后刷新页面。</li><li><b>加载时出现清单或 service worker 错误</b>：加载的是占位用的 manifest.json。请把对应浏览器的清单文件复制覆盖它（第 2 步），然后重新加载文件夹。</li><li><b>Firefox 中扩展消失了</b>：临时附加组件会在重启时被移除，请重新加载。</li><li><b>下载被阻止</b>：如果浏览器询问，请允许该网站下载多个文件。</li></ul>",
            },
            "ext_open_releases": {
                "english": "Release Page",
                "japanese": "リリースページ",
                "korean": "릴리스 페이지",
                "chinese-simplified": "发布页面",
            },
            "ext_open_folder": {
                "english": "Extension Folder on GitHub",
                "japanese": "GitHub の拡張機能フォルダ",
                "korean": "GitHub의 확장 프로그램 폴더",
                "chinese-simplified": "GitHub 上的扩展文件夹",
            },
            "ext_copy_command": {
                "english": "Copy",
                "japanese": "コピー",
                "korean": "복사",
                "chinese-simplified": "复制",
            },
            "ext_copied": {
                "english": "Copied!",
                "japanese": "コピーしました",
                "korean": "복사됨",
                "chinese-simplified": "已复制",
            },
            # Proxy settings
            "proxy_intro": {
                "english": "Send downloads through your own proxy server or the Tor network.",
                "japanese": "ダウンロードを自分のプロキシサーバーまたは Tor ネットワーク経由で行います。",
                "korean": "다운로드를 직접 지정한 프록시 서버나 Tor 네트워크를 통해 보냅니다.",
                "chinese-simplified": "通过你自己的代理服务器或 Tor 网络进行下载。",
            },
            "custom_proxy_hint": {
                "english": "Accepts host:port, http://host:port or socks5h://host:port. Add user:password@ before the host if the proxy needs a login.",
                "japanese": "host:port、http://host:port、socks5h://host:port の形式に対応しています。ログインが必要なプロキシでは、ホストの前に user:password@ を付けてください。",
                "korean": "host:port, http://host:port, socks5h://host:port 형식을 지원합니다. 로그인이 필요한 프록시라면 호스트 앞에 user:password@를 붙이세요.",
                "chinese-simplified": "支持 host:port、http://host:port 或 socks5h://host:port 格式。如果代理需要登录，请在主机前加上 user:password@。",
            },
            "tor_hint": {
                "english": "Downloads go through Tor (port 9050), including a Tor service you run yourself. If Tor isn't running, downloads fail instead of using your own connection.",
                "japanese": "ダウンロードは Tor（ポート 9050）を経由します。自分で実行している Tor サービスも使えます。Tor が動いていない場合、自分の接続を使わずにダウンロードは失敗します。",
                "korean": "다운로드는 Tor(포트 9050)를 통해 이루어지며, 직접 실행 중인 Tor 서비스도 사용할 수 있습니다. Tor가 실행 중이 아니면 내 연결을 사용하지 않고 다운로드가 실패합니다.",
                "chinese-simplified": "下载会通过 Tor（端口 9050）进行，也可以使用你自己运行的 Tor 服务。如果 Tor 未运行，下载会失败，而不会使用你自己的网络连接。",
            },
            # Full logs window
            "copy_logs": {
                "english": "Copy All",
                "japanese": "すべてコピー",
                "korean": "모두 복사",
                "chinese-simplified": "全部复制",
            },
            "logs_copied": {
                "english": "Copied!",
                "japanese": "コピーしました",
                "korean": "복사됨",
                "chinese-simplified": "已复制",
            },
            "logs_search_placeholder": {
                "english": "Search logs…",
                "japanese": "ログを検索…",
                "korean": "로그 검색…",
                "chinese-simplified": "搜索日志…",
            },
            "logs_find_previous": {
                "english": "Previous match (Shift+Enter)",
                "japanese": "前の一致 (Shift+Enter)",
                "korean": "이전 결과 (Shift+Enter)",
                "chinese-simplified": "上一个匹配（Shift+Enter）",
            },
            "logs_find_next": {
                "english": "Next match (Enter)",
                "japanese": "次の一致 (Enter)",
                "korean": "다음 결과 (Enter)",
                "chinese-simplified": "下一个匹配（Enter）",
            },
            "logs_match_count": {
                "english": "{0} matches",
                "japanese": "{0}件一致",
                "korean": "{0}개 일치",
                "chinese-simplified": "{0} 个匹配",
            },
            "logs_match_count_one": {
                "english": "1 match",
                "japanese": "1件一致",
                "korean": "1개 일치",
                "chinese-simplified": "1 个匹配",
            },
            "logs_no_matches": {
                "english": "No matches",
                "japanese": "一致なし",
                "korean": "일치 항목 없음",
                "chinese-simplified": "无匹配",
            },
            "logs_line_count": {
                "english": "{0} lines",
                "japanese": "{0}行",
                "korean": "{0}줄",
                "chinese-simplified": "{0} 行",
            },
            "logs_line_count_one": {
                "english": "1 line",
                "japanese": "1行",
                "korean": "1줄",
                "chinese-simplified": "1 行",
            },
            "logs_jump_to_latest": {
                "english": "Jump to Latest",
                "japanese": "最新へ移動",
                "korean": "최신으로 이동",
                "chinese-simplified": "跳到最新",
            },
            "logs_new_lines": {
                "english": "{0} New Lines",
                "japanese": "新しい行 {0}件",
                "korean": "새 줄 {0}개",
                "chinese-simplified": "{0} 条新日志",
            },
            "logs_new_lines_one": {
                "english": "1 New Line",
                "japanese": "新しい行 1件",
                "korean": "새 줄 1개",
                "chinese-simplified": "1 条新日志",
            },
            "logs_follow_tooltip": {
                "english": "Auto-scroll pauses while you scroll up and resumes when you reach the bottom.",
                "japanese": "上にスクロールすると自動スクロールが一時停止し、一番下まで戻ると再開します。",
                "korean": "위로 스크롤하면 자동 스크롤이 일시 중지되고, 맨 아래로 돌아오면 다시 시작됩니다.",
                "chinese-simplified": "向上滚动时自动滚动会暂停，回到底部后自动恢复。",
            },
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

    def get_language(self):
        """
        Get the current language (alias for get_current_language).

        Returns:
            str: Current language
        """
        return self.get_current_language()

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
