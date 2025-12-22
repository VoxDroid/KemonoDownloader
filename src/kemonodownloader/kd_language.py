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
                "chinese-simplified": "从 .txt 文件添加链接。每个链接应位于新行上。"
            },
            "add_links_from_file_title": {
                "english": "Import from TXT File.",
                "japanese": "TXTファイルからインポート。",
                "korean": "TXT 파일에서 가져오기.",
                "chinese-simplified": "从 TXT 文件导入。"
            },
            
            "select_links_file": {
                "english": "Select .txt file containing creator URLs",
                "japanese": ".txtファイルからクリエイターのURLを含むファイルを選択してください",
                "korean": ".txt 파일에서 크리에이터 URL을 포함하는 파일을 선택하세요",
                "chinese-simplified": "选择包含创作者URL的.txt文件"
            },
            
            "url_already_in_queue": {
                "english": "URL is already in the download queue",
                "japanese": "URLはすでにダウンロードキューにあります",
                "korean": "URL은 이미 다운로드 대기열에 있습니다",
                "chinese-simplified": "URL已在下载队列中"
            },
            
            "added_to_queue": {
                "english": "Added to queue",
                "japanese": "キューに追加されました",
                "korean": "대기열에 추가됨",
                "chinese-simplified": "已添加到队列"
            },
            
            "invalid_url_format_from_txt": {
                "english": "Invalid URL format, skipping",
                "japanese": "無効なURL形式、スキップします",
                "korean": "잘못된 URL 형식, 건너뜁니다",
                "chinese-simplified": "无效的URL格式，跳过"
            },
            
            "error_processing_url": {
                "english": "Error processing URL",
                "japanese": "URL処理中にエラーが発生しました",
                "korean": "URL 처리 중 오류 발생",
                "chinese-simplified": "处理URL时出错"
            },
            
            "bulk_add_summary": {
                "english": "Added {0} link(s) to queue. Skipped {1} link(s).",
                "japanese": "キューに {0} 件のリンクを追加しました。{1} 件のリンクをスキップしました。",
                "korean": "대기열에 {0}개의 링크를 추가했습니다. {1}개의 링크를 건너뛰었습니다.",
                "chinese-simplified": "已将 {0} 个链接添加到队列。跳过了 {1} 个链接。"
            },
            
            "bulk_add_complete": { 
                "english": "Bulk Add Complete",
                "japanese": "一括追加完了",
                "korean": "대량 추가 완료",
                "chinese-simplified": "批量添加完成"
            },
            
            "file_read_error": {
                "english": "Error reading file: {0}",
                "japanese": "ファイルの読み取りエラー：{0}",
                "korean": "파일 읽기 오류: {0}",
                "chinese-simplified": "读取文件时出错：{0}"
            },
            
            "file_read_error_title": {
                "english": "File Read Error",
                "japanese": "ファイル読み取りエラー",
                "korean": "파일 읽기 오류",
                "chinese-simplified": "文件读取错误"
            },

            # Log Texts
            "checking_creator_with_url": {
                "english": "Checking creator with URL: {0}",
                "japanese": "URL を使用してクリエイターを確認中: {0}",
                "korean": "URL로 크리에이터 확인 중: {0}",
                "chinese-simplified": "正在检查创作者，URL：{0}"
            },

            "parsed_url_service_creator": {
                "english": "Parsed URL - Service: {0}, Creator ID: {1}",
                "japanese": "解析したURL - サービス: {0}, クリエイターID: {1}",
                "korean": "URL 해석됨 - 서비스: {0}, 크리에이터 ID: {1}",
                "chinese-simplified": "已解析URL - 服务：{0}, 创作者ID：{1}"
            },

            "base_api_url": {
                "english": "Base API URL: {0}",
                "japanese": "ベースAPI URL: {0}",
                "korean": "기본 API URL: {0}",
                "chinese-simplified": "基础 API URL：{0}"
            },
            
            "successfully_validated_url": {
                "english": "Successfully validated URL {0}",
                "japanese": "URL {0} を正常に検証しました",
                "korean": "URL {0}을 성공적으로 검증했습니다",
                "chinese-simplified": "成功验证了URL {0}"
            },
            
            "thread_deleted_during_cancellation_wait": {
                "english": "A thread was deleted during cancellation wait",
                "japanese": "キャンセル待機中にスレッドが削除されました",
                "korean": "취소 대기 중 스레드가 삭제되었습니다",
                "chinese-simplified": "在取消等待期间，一个线程被删除了"
            },
            
            "thread_not_exited_gracefully": {
                "english": "Thread {0} did not exit gracefully, attempting termination.",
                "japanese": "スレッド {0} は正常に終了しませんでした。強制終了を試みます。",
                "korean": "스레드 {0} 가 정상적으로 종료되지 않았습니다. 강제 종료를 시도합니다.",
                "chinese-simplified": "线程 {0} 未正常退出，正在尝试终止。"
            },

            "terminated_thread": {
                "english": "Terminated thread: {0}",
                "japanese": "終了したスレッド: {0}",
                "korean": "종료된 스레드: {0}",
                "chinese-simplified": "已终止线程：{0}"
            },
            
            "filtered_post": {
                "english": "Filtered post: {0} (ID: {1})",
                "japanese": "フィルタリングされた投稿：{0}（ID：{1}）",
                "korean": "필터링된 게시물: {0} (ID: {1})",
                "chinese-simplified": "已过滤的帖子：{0}（ID：{1}）"
            },
            
            "creator_download_thread_started": {
                "english": "CreatorDownloadThread started for service: {0}, creator_id: {1}",
                "japanese": "サービス {0}、クリエイターID {1} のためにCreatorDownloadThreadを開始しました",
                "korean": "서비스 {0}, 크리에이터 ID {1}에 대해 CreatorDownloadThread를 시작했습니다",
                "chinese-simplified": "为服务 {0}，创建者ID {1} 启动了CreatorDownloadThread"
            },
            "total_posts": {
                "english": "Total posts: {0}",
                "japanese": "投稿の合計：{0}",
                "korean": "총 게시물 수: {0}",
                "chinese-simplified": "帖子总数：{0}"
            },
            "failed_to_create_creator_folder": {
                "english": "Failed to create creator folder {0}: {1}",
                "japanese": "クリエイターフォルダ {0} の作成に失敗しました：{1}",
                "korean": "크리에이터 폴더 {0} 생성에 실패했습니다: {1}",
                "chinese-simplified": "无法创建创建者文件夹 {0}：{1}"
            },
            "created_directory": {
                "english": "Created directory: {0}",
                "japanese": "ディレクトリを作成しました：{0}",
                "korean": "디렉토리를 생성했습니다: {0}",
                "chinese-simplified": "已创建目录：{0}"
            },
            "total_selected_files_to_download": {
                "english": "Total selected files to download: {0}",
                "japanese": "ダウンロードする選択済みファイルの合計：{0}",
                "korean": "다운로드할 선택된 총 파일 수: {0}",
                "chinese-simplified": "选择的要下载的文件总数：{0}"
            },
            
            "error_in_async_download_loop": {
                "english": "Error in async download loop: {0}",
                "japanese": "非同期ダウンロードループでのエラー：{0}",
                "korean": "비동기 다운로드 루프에서 오류: {0}",
                "chinese-simplified": "异步下载循环错误：{0}"
            },
            "no_files_selected_for_download": {
                "english": "No files selected for download.",
                "japanese": "ダウンロードするファイルが選択されていません。",
                "korean": "다운로드할 파일이 선택되지 않았습니다.",
                "chinese-simplified": "未选择要下载的文件。"
            },
            "download_completed_with_failed_files": {
                "english": "Download completed with {0} failed files:",
                "japanese": "ダウンロードが完了しました、{0} 件のファイルが失敗：",
                "korean": "다운로드가 완료되었습니다, {0}개의 파일이 실패했습니다:",
                "chinese-simplified": "下载完成，{0} 个文件失败："
            },
            "failed_to_download_file": {
                "english": "Failed to download {0}: {1}",
                "japanese": "{0} のダウンロードに失敗しました：{1}",
                "korean": "{0} 다운로드에 실패했습니다: {1}",
                "chinese-simplified": "无法下载 {0}：{1}"
            },
            
            "checking_main_file": {
                "english": "Checking main file: {0} ({1})",
                "japanese": "メインファイルを確認中：{0}（{1}）",
                "korean": "메인 파일 확인 중: {0} ({1})",
                "chinese-simplified": "正在检查主文件：{0}（{1}）"
            },
            "added_main_file": {
                "english": "Added main file: {0}",
                "japanese": "メインファイルを追加しました：{0}",
                "korean": "메인 파일을 추가했습니다: {0}",
                "chinese-simplified": "已添加主文件：{0}"
            },
            
            "checking_attachment": {
                "english": "Checking attachment: {0} ({1})",
                "japanese": "添付ファイルを確認中：{0}（{1}）",
                "korean": "첨부 파일 확인 중: {0} ({1})",
                "chinese-simplified": "正在检查附件：{0}（{1}）"
            },
            "added_attachment": {
                "english": "Added attachment: {0}",
                "japanese": "添付ファイルを追加しました：{0}",
                "korean": "첨부 파일을 추가했습니다: {0}",
                "chinese-simplified": "已添加附件：{0}"
            },
            
            "detecting_files_for_post": {
                "english": "Detecting files for post with allowed extensions: {0}",
                "japanese": "許可された拡張子で投稿のファイルを検出中：{0}",
                "korean": "허용된 확장자로 게시물의 파일을 감지 중: {0}",
                "chinese-simplified": "正在检测具有允许扩展名的帖子文件：{0}"
            },
            
            "thread_already_deleted_during_termination": {
                "english": "Thread {0} already deleted during termination",
                "japanese": "スレッド {0} は終了処理中にすでに削除されています",
                "korean": "스레드 {0} 는 종료 처리 중 이미 삭제되었습니다",
                "chinese-simplified": "线程 {0} 在终止过程中已被删除"
            },

            "cancellation_process_completed": {
                "english": "Cancellation process completed",
                "japanese": "キャンセル処理が完了しました",
                "korean": "취소 프로세스가 완료되었습니다",
                "chinese-simplified": "取消过程已完成"
            },
            
            "checkbox_toggle_finished": {
                "english": "Checkbox toggle finished, checked posts: {0}, visible posts: {1}",
                "japanese": "チェックボックスの切り替えが完了しました。チェックされた投稿: {0}, 表示された投稿: {1}",
                "korean": "체크박스 전환이 완료되었습니다. 선택된 게시물: {0}, 표시된 게시물: {1}",
                "chinese-simplified": "复选框切换完成，已选帖子：{0}, 可见帖子：{1}"
            },
            
            "no_current_creator_url_set": {
                "english": "No current creator URL set.",
                "japanese": "現在のクリエイターURLが設定されていません。",
                "korean": "현재 제작자 URL이 설정되지 않았습니다.",
                "chinese-simplified": "未设置当前创作者 URL。"
            },
            
            "no_posts_selected_for_creator": {
                "english": "No posts selected for {0}. Checked URLs: {1}",
                "japanese": "{0} に対して投稿が選択されていません。確認済みURL: {1}",
                "korean": "{0}에 대해 선택된 게시물이 없습니다. 확인된 URL: {1}",
                "chinese-simplified": "未为 {0} 选择任何帖子。已检查的 URL：{1}"
            },
            
            "no_visible_posts_to_toggle": {
                "english": "No visible posts to toggle.",
                "japanese": "切り替える表示可能な投稿がありません。",
                "korean": "전환할 수 있는 표시된 게시물이 없습니다.",
                "chinese-simplified": "没有可切换的可见帖子。"
            },
            "no_posts_to_toggle": {
                "english": "No posts to toggle.",
                "japanese": "切り替える投稿がありません。",
                "korean": "전환할 게시물이 없습니다.",
                "chinese-simplified": "没有可切换的帖子。"
            },
            
            "download_completed_with_failed_files": {
                "english": "Download completed with {0} failed files:",
                "japanese": "ダウンロードが完了しましたが、{0} 件のファイルが失敗しました:",
                "korean": "다운로드가 완료되었지만 {0}개의 파일이 실패했습니다:",
                "chinese-simplified": "下载完成，但有 {0} 个文件失败："
            },
            "download_file_failed_with_error": {
                "english": "Failed to download {0}: {1}",
                "japanese": "{0} のダウンロードに失敗しました: {1}",
                "korean": "{0} 다운로드 실패: {1}",
                "chinese-simplified": "下载 {0} 失败：{1}"
            },
            
            "checkbox_toggle_already_in_progress": {
                "english": "Checkbox toggle already in progress. Please wait.",
                "japanese": "チェックボックスの切り替えはすでに進行中です。しばらくお待ちください。",
                "korean": "체크박스 전환이 이미 진행 중입니다. 잠시만 기다려 주세요.",
                "chinese-simplified": "复选框切换已在进行中。请稍候。"
            },
            
            "all_posts_and_files_completed": {
                "english": "All posts and files completed for current creator.",
                "japanese": "現在のクリエイターのすべての投稿とファイルが完了しました。",
                "korean": "현재 제작자의 모든 게시물과 파일이 완료되었습니다.",
                "chinese-simplified": "当前创作者的所有帖子和文件已完成。"
            },
            
            "overall_progress_updated": {
                "english": "Overall progress updated: {0}/{1} files, {2}%",
                "japanese": "全体の進捗が更新されました: {0}/{1} ファイル, {2}%",
                "korean": "전체 진행 상황이 업데이트되었습니다: {0}/{1} 파일, {2}%",
                "chinese-simplified": "总体进度已更新：{0}/{1} 个文件，{2}%"
            },
            
            "filtering_already_in_progress": {
                "english": "Filtering already in progress. Please wait.",
                "japanese": "フィルタリングはすでに進行中です。しばらくお待ちください。",
                "korean": "필터링이 이미 진행 중입니다. 잠시만 기다려 주세요.",
                "chinese-simplified": "筛选已在进行中。请稍候。"
            },
            
            "filtering_completed_displayed_posts": {
                "english": "Filtering completed, displayed {0} posts",
                "japanese": "フィルタリングが完了しました。表示された投稿数: {0}",
                "korean": "필터링이 완료되었습니다. 표시된 게시물: {0}",
                "chinese-simplified": "筛选完成，显示了 {0} 个帖子"
            },
            "displayed_page_posts": {
                "english": "Displayed page {0} with {1} posts",
                "japanese": "ページ {0} を表示（投稿数: {1}）",
                "korean": "페이지 {0} 표시（게시물: {1}）",
                "chinese-simplified": "显示第 {0} 页（{1} 个帖子）"
            },
            
            "no_post_id_found_for_title": {
                "english": "No post ID found for title: {0}",
                "japanese": "タイトルに対応する投稿IDが見つかりません: {0}",
                "korean": "제목에 대한 게시물 ID를 찾을 수 없습니다: {0}",
                "chinese-simplified": "未找到标题对应的帖子 ID：{0}"
            },
            
            "updated_checked_posts_count": {
                "english": "Updated checked posts count: {0}, checked_urls: {1}, all_detected: {2}, selected IDs: {3}",
                "japanese": "チェック済み投稿数を更新しました: {0}, 確認済みURL: {1}, 検出された全件: {2}, 選択されたID: {3}",
                "korean": "체크된 게시물 수가 업데이트되었습니다: {0}, 확인된 URL: {1}, 감지된 전체: {2}, 선택된 ID: {3}",
                "chinese-simplified": "已更新已检查帖子数：{0}, 已检查 URL：{1}, 检测到的总数：{2}, 已选择的 ID：{3}"
            },
            
            "trying_endpoint": {
                "english": "Trying endpoint: {0}",
                "japanese": "エンドポイントを試しています: {0}",
                "korean": "엔드포인트 시도 중: {0}",
                "chinese-simplified": "正在尝试端点：{0}"
            },
            
            "reached_last_page": {
                "english": "Reached last page for creator {0}. Total posts fetched: {1}",
                "japanese": "クリエイター {0} の最後のページに到達しました。取得した投稿の合計：{1}",
                "korean": "크리에이터 {0}의 마지막 페이지에 도달했습니다. 가져온 총 게시물 수: {1}",
                "chinese-simplified": "已到达创建者 {0} 的最后一页。获取的帖子总数：{1}"
            },
            "all_api_endpoints_failed": {
                "english": "All API endpoints failed for creator {0}",
                "japanese": "クリエイター {0} のすべてのAPIエンドポイントが失敗しました",
                "korean": "크리에이터 {0}의 모든 API 엔드포인트가 실패했습니다",
                "chinese-simplified": "创建者 {0} 的所有API端点均失败"
            },
            
            "successfully_decompressed_gzipped_response": {
                "english": "Successfully decompressed gzipped response",
                "japanese": "gzipped応答の解凍に成功しました",
                "korean": "gzipped 응답을 성공적으로 압축 해제했습니다",
                "chinese-simplified": "成功解压gzipped响应"
            },
            "gzip_decompression_failed": {
                "english": "Gzip decompression failed, trying plain text: {0}",
                "japanese": "Gzip解凍に失敗しました、プレーンテキストを試みます：{0}",
                "korean": "Gzip 압축 해제에 실패했습니다, 일반 텍스트를 시도합니다: {0}",
                "chinese-simplified": "Gzip解压失败，尝试纯文本：{0}"
            },
            
            "empty_response_at_offset": {
                "english": "Empty response at offset {0}. No more posts available.",
                "japanese": "オフセット {0} で空の応答。投稿がこれ以上ありません。",
                "korean": "오프셋 {0}에서 빈 응답. 더 이상 게시물이 없습니다.",
                "chinese-simplified": "在偏移量 {0} 处收到空响应。没有更多帖子可用。"
            },
            
            "failed_to_parse_response": {
                "english": "Failed to parse response: {0}",
                "japanese": "応答の解析に失敗しました：{0}",
                "korean": "응답 파싱에 실패했습니다: {0}",
                "chinese-simplified": "解析响应失败：{0}"
            },
            "response_content_first_500_chars": {
                "english": "Response content (first 500 chars): {0}",
                "japanese": "応答内容（最初の500文字）：{0}",
                "korean": "응답 내용 (처음 500자): {0}",
                "chinese-simplified": "响应内容（前500个字符）：{0}"
            },
            "using_cached_posts_fallback": {
                "english": "Fetching failed, using cached posts for {0}",
                "japanese": "取得に失敗しました、{0}のキャッシュされた投稿を使用します",
                "korean": "가져오기에 실패하여 {0}의 캐시된 게시물을 사용합니다",
                "chinese-simplified": "获取失败，使用 {0} 的缓存帖子"
            },
            
            "endpoint_successful": {
                "english": "Endpoint successful: {0}",
                "japanese": "エンドポイントに成功しました: {0}",
                "korean": "엔드포인트 성공: {0}",
                "chinese-simplified": "端点成功：{0}"
            },
            "endpoint_returned_status_likely_end": {
                "english": "Endpoint returned {0} (likely reached end of data): {1}",
                "japanese": "エンドポイントが {0} を返しました（データの終端に到達した可能性あり）: {1}",
                "korean": "엔드포인트가 {0}을(를) 반환했습니다 (데이터 끝에 도달했을 가능성 있음): {1}",
                "chinese-simplified": "端点返回 {0}（可能已到达数据末尾）：{1}"
            },
            "endpoint_failed_with_status": {
                "english": "Endpoint failed: {0} - Status: {1}",
                "japanese": "エンドポイントに失敗しました: {0} - ステータス: {1}",
                "korean": "엔드포인트 실패: {0} - 상태: {1}",
                "chinese-simplified": "端点失败：{0} - 状态：{1}"
            },
            "endpoint_unavailable_likely_end": {
                "english": "Endpoint unavailable (likely reached end of data): {0} - {1}",
                "japanese": "エンドポイントが利用できません（データの終端に到達した可能性あり）: {0} - {1}",
                "korean": "엔드포인트를 사용할 수 없습니다 (데이터 끝에 도달했을 가능성 있음): {0} - {1}",
                "chinese-simplified": "端点不可用（可能已到达数据末尾）：{0} - {1}"
            },
            "endpoint_error_with_exception": {
                "english": "Endpoint error: {0} - {1}",
                "japanese": "エンドポイントエラー: {0} - {1}",
                "korean": "엔드포인트 오류: {0} - {1}",
                "chinese-simplified": "端点错误：{0} - {1}"
            },
            
            "validation_attempt_failed": {
                "english": "Validation attempt {0} failed, retrying in {1}s...",
                "japanese": "検証試行 {0} が失敗しました、{1}秒後に再試行します...",
                "korean": "검증 시도 {0}이 실패했습니다, {1}초 후에 재시도합니다...",
                "chinese-simplified": "验证尝试 {0} 失败，将在 {1}秒后重试..."
            },
            
            "unexpected_response_structure": {
                "english": "Unexpected response structure: {0}",
                "japanese": "予期しない応答構造：{0}",
                "korean": "예상치 못한 응답 구조: {0}",
                "chinese-simplified": "意外的响应结构：{0}"
            },
            
            "invalid_posts_data_type": {
                "english": "Invalid posts data type: {0}",
                "japanese": "無効な投稿データ型：{0}",
                "korean": "잘못된 게시물 데이터 유형: {0}",
                "chinese-simplified": "无效的帖子数据类型：{0}"
            },
            
            "no_more_posts_at_offset": {
                "english": "No more posts to fetch at offset {0}. Stopping pagination.",
                "japanese": "オフセット {0} で取得する投稿がありません。ページネーションを停止します。",
                "korean": "오프셋 {0}에서 가져올 게시물이 없습니다. 페이지네이션을 중지합니다.",
                "chinese-simplified": "在偏移量 {0} 处没有更多帖子可获取。停止分页。"
            },
            "last_page_reached_with_counts": {
                "english": "Last page reached (received {0} posts, expected {1}). Total posts fetched: {2}",
                "japanese": "最後のページに到達しました（{0} 件の投稿を受信、{1} 件を期待）。取得した投稿の合計：{2}",
                "korean": "마지막 페이지에 도달했습니다 ({0}개의 게시물 수신, {1}개 예상). 가져온 총 게시물 수: {2}",
                "chinese-simplified": "已到达最后一页（收到 {0} 个帖子，预期 {1} 个）。获取的帖子总数：{2}"
            },
            
            "mapped_title_to_id_and_thumbnail": {
                "english": "Mapped title '{0}' to ID: {1}, Thumbnail: {2}",
                "japanese": "タイトル '{0}' をID：{1}、サムネイル：{2} にマッピングしました",
                "korean": "제목 '{0}'을(를) ID: {1}, 썸네일: {2}에 매핑했습니다",
                "chinese-simplified": "将标题 '{0}' 映射到ID：{1}，缩略图：{2}"
            },
            "prepared_posts_for_population": {
                "english": "Prepared {0} posts for population, unique titles: {1}",
                "japanese": "{0} 件の投稿を入力用に準備しました、ユニークなタイトル数：{1}",
                "korean": "{0}개의 게시물을 채우기 위해 준비했습니다, 고유 제목 수: {1}",
                "chinese-simplified": "为填充准备了 {0} 个帖子，唯一标题数：{1}"
            },
            
            "total_posts_fetched_for_creator": {
                "english": "Total posts fetched for creator {0}: {1}",
                "japanese": "クリエイター {0} のために取得した投稿の合計：{1}",
                "korean": "크리에이터 {0}에 대해 가져온 총 게시물 수: {1}",
                "chinese-simplified": "为创建者 {0} 获取的帖子总数：{1}"
            },
            
            "checking_content_image": {
                "english": "Checking content image: {0} ({1})",
                "japanese": "コンテンツ画像を確認中：{0}（{1}）",
                "korean": "콘텐츠 이미지 확인 중: {0} ({1})",
                "chinese-simplified": "正在检查内容图像：{0}（{1}）"
            },
            "added_content_image": {
                "english": "Added content image: {0}",
                "japanese": "コンテンツ画像を追加しました：{0}",
                "korean": "콘텐츠 이미지를 추가했습니다: {0}",
                "chinese-simplified": "已添加内容图像：{0}"
            },
            "total_files_detected": {
                "english": "Total files detected: {0}",
                "japanese": "検出されたファイルの合計：{0}",
                "korean": "감지된 총 파일 수: {0}",
                "chinese-simplified": "检测到的文件总数：{0}"
            },
            
            "total_files_to_download": {
                "english": "Total files to download: {0}",
                "japanese": "ダウンロードするファイルの合計：{0}",
                "korean": "다운로드할 총 파일 수: {0}",
                "chinese-simplified": "要下载的文件总数：{0}"
            },
            
            "failed_to_fetch_creator_name": {
                "english": "Failed to fetch creator name, using default: {0}",
                "japanese": "クリエイター名の取得に失敗しました、デフォルトを使用：{0}",
                "korean": "크리에이터 이름을 가져오지 못했습니다, 기본값 사용: {0}",
                "chinese-simplified": "无法获取创建者名称，使用默认值：{0}"
            },
            "error_fetching_creator_name": {
                "english": "Error fetching creator name: {0}",
                "japanese": "クリエイター名の取得エラー：{0}",
                "korean": "크리에이터 이름 가져오기 오류: {0}",
                "chinese-simplified": "获取创建者名称出错：{0}"
            },
            
            "fetched_title_for_post": {
                "english": "Fetched title for post {0}: {1}",
                "japanese": "投稿 {0} のタイトルを取得しました：{1}",
                "korean": "게시물 {0}의 제목을 가져왔습니다: {1}",
                "chinese-simplified": "获取了帖子 {0} 的标题：{1}"
            },
            "failed_to_fetch_title_for_post": {
                "english": "Failed to fetch title for post {0}, using default",
                "japanese": "投稿 {0} のタイトル取得に失敗しました、デフォルトを使用",
                "korean": "게시물 {0}의 제목을 가져오지 못했습니다, 기본값 사용",
                "chinese-simplified": "无法获取帖子 {0} 的标题，使用默认值"
            },
            "error_fetching_title_for_post": {
                "english": "Error fetching title for post {0}: {1}",
                "japanese": "投稿 {0} のタイトル取得エラー：{1}",
                "korean": "게시물 {0}의 제목 가져오기 오류: {1}",
                "chinese-simplified": "获取帖子 {0} 的标题出错：{1}"
            },
            
            "failed_to_create_post_folder": {
                "english": "Failed to create post folder {0}: {1}. Likely due to invalid folder name.",
                "japanese": "投稿フォルダ {0} の作成に失敗しました：{1}。フォルダ名が無効な可能性があります。",
                "korean": "게시물 폴더 {0} 생성에 실패했습니다: {1}. 폴더 이름이 유효하지 않을 가능성이 있습니다.",
                "chinese-simplified": "无法创建帖子文件夹 {0}：{1}。可能是由于文件夹名称无效。"
            },
            
            "failed_to_remove_interrupted_file": {
                "english": "Failed to remove interrupted file {0}: {1}",
                "japanese": "中断されたファイル {0} の削除に失敗しました：{1}",
                "korean": "중단된 파일 {0} 제거에 실패했습니다: {1}",
                "chinese-simplified": "无法删除中断的文件 {0}：{1}"
            },
            
            "unexpected_error_downloading": {
                "english": "Unexpected error downloading {0}: {1}",
                "japanese": "{0} のダウンロード中に予期しないエラー：{1}",
                "korean": "{0} 다운로드 중 예기치 않은 오류: {1}",
                "chinese-simplified": "下载 {0} 时发生意外错误：{1}"
            },
            
            "error_in_download_worker": {
                "english": "Error in download worker: {0}",
                "japanese": "ダウンロードワーカーでのエラー：{0}",
                "korean": "다운로드 작업자 오류: {0}",
                "chinese-simplified": "下载工作进程错误：{0}"
            },
            
            "failed_to_load_file_hashes": {
                "english": "Failed to load file hashes: {0}",
                "japanese": "ファイルハッシュの読み込みに失敗しました：{0}",
                "korean": "파일 해시 로드에 실패했습니다: {0}",
                "chinese-simplified": "无法加载文件哈希：{0}"
            },
            "failed_to_save_file_hashes": {
                "english": "Failed to save file hashes: {0}",
                "japanese": "ファイルハッシュの保存に失敗しました：{0}",
                "korean": "파일 해시 저장에 실패했습니다: {0}",
                "chinese-simplified": "无法保存文件哈希：{0}"
            },
            
            "rate_limit_hit": {
                "english": "Rate limit hit for {0} (attempt {1}/{2}). Retrying...",
                "japanese": "{0} のレート制限に達しました（試行 {1}/{2}）。再試行中...",
                "korean": "{0}에 대한 속도 제한에 도달했습니다 (시도 {1}/{2}). 재시도 중...",
                "chinese-simplified": "{0} 的速率限制已达到（尝试 {1}/{2}）。正在重试..."
            },
            "trying_again_in": {
                "english": "Trying again in {0}",
                "japanese": "{0}秒後に再試行します",
                "korean": "{0}초 후에 다시 시도합니다",
                "chinese-simplified": "{0}秒后再次尝试"
            },
            "failed_to_fetch_api": {
                "english": "Failed to fetch {0} - Status code: {1}",
                "japanese": "{0} の取得に失敗しました - ステータスコード：{1}",
                "korean": "{0} 가져오기에 실패했습니다 - 상태 코드: {1}",
                "chinese-simplified": "无法获取 {0} - 状态码：{1}"
            },
            "post_data_for_id": {
                "english": "Post data for {0}: {1}",
                "japanese": "{0} の投稿データ：{1}",
                "korean": "{0}에 대한 게시물 데이터: {1}",
                "chinese-simplified": "{0} 的帖子数据：{1}"
            },
            
            "error_fetching_post_max_attempts": {
                "english": "Error fetching post {0} after {1} attempts: {2}",
                "japanese": "投稿 {0} の取得エラー、{1} 回試行後：{2}",
                "korean": "게시물 {0} 가져오기 오류, {1}번 시도 후: {2}",
                "chinese-simplified": "获取帖子 {0} 出错，经过 {1} 次尝试：{2}"
            },
            "error_fetching_post": {
                "english": "Error fetching post {0} (attempt {1}/{2}): {3}. Retrying...",
                "japanese": "投稿 {0} の取得エラー（試行 {1}/{2}）：{3}。再試行中...",
                "korean": "게시물 {0} 가져오기 오류 (시도 {1}/{2}): {3}. 재시도 중...",
                "chinese-simplified": "获取帖子 {0} 出错（尝试 {1}/{2}）：{3}。正在重试..."
            },
            "trying_again_in": {
                "english": "Trying again in {0}",
                "japanese": "{0}秒後に再試行します",
                "korean": "{0}초 후에 다시 시도합니다",
                "chinese-simplified": "{0}秒后再次尝试"
            },
            
            "allowed_extensions_for_download": {
                "english": "Allowed extensions for download: {0}",
                "japanese": "ダウンロードの許可された拡張子：{0}",
                "korean": "다운로드 허용된 확장자: {0}",
                "chinese-simplified": "允许下载的扩展名：{0}"
            },
            
            "no_matching_creator_urls": {
                "english": "No matching creator URLs found for selected posts.",
                "japanese": "選択した投稿に対応するクリエイターのURLが見つかりませんでした。",
                "korean": "선택한 게시물에 대해 일치하는 크리에이터 URL을 찾을 수 없습니다.",
                "chinese-simplified": "未找到与所选帖子匹配的创建者URL。"
            },
            
            "fetched_posts_at_offset": {
                "english": "Fetched {0} posts at offset {1}",
                "japanese": "オフセット {1} で {0} 件の投稿を取得しました",
                "korean": "오프셋 {1}에서 {0}개의 게시물을 가져왔습니다",
                "chinese-simplified": "在偏移量 {1} 处获取了 {0} 个帖子"
            },
            "received_less_than_page_size": {
                "english": "Received {0} posts (less than page size {1}), indicating last page reached",
                "japanese": "{0} 件の投稿を受信しました（ページサイズ {1} 未満）、最後のページに到達したことを示します",
                "korean": "{0}개의 게시물을 수신했습니다 (페이지 크기 {1} 미만), 마지막 페이지에 도달했음을 나타냅니다",
                "chinese-simplified": "接收到 {0} 个帖子（少于页面大小 {1}），表明已到达最后一页"
            },
            "post_id_and_title": {
                "english": "Post ID: {0}, Title: {1}",
                "japanese": "投稿ID：{0}、タイトル：{1}",
                "korean": "게시물 ID: {0}, 제목: {1}",
                "chinese-simplified": "帖子ID：{0}，标题：{1}"
            },
            
            "network_error_attempt": {
                "english": "Network error on attempt {0}: {1}, retrying...",
                "japanese": "試行 {0} でネットワークエラー：{1}、再試行中...",
                "korean": "시도 {0}에서 네트워크 오류: {1}, 재시도 중...",
                "chinese-simplified": "尝试 {0} 时网络错误：{1}，正在重试..."
            },
            
            "failed_to_validate": {
                "english": "Failed to validate {0} after {1} attempts: {2}",
                "japanese": "{0} の検証に {1} 回試行後失敗しました：{2}",
                "korean": "{0} 검증이 {1}번 시도 후 실패했습니다: {2}",
                "chinese-simplified": "在 {1} 次尝试后无法验证 {0}：{2}"
            },
            
            "validation_in_progress": {
                "english": "Validation already in progress. Please wait.",
                "japanese": "検証がすでに進行中です。しばらくお待ちください。",
                "korean": "검증이 이미 진행 중입니다. 잠시 기다려 주세요.",
                "chinese-simplified": "验证已在进行中。请稍等。"
            },
            
            "checkbox_toggled_for_post": {
                "english": "Checkbox toggled for post {0} (ID: {1}) to {2}",
                "japanese": "投稿 {0} (ID: {1}) のチェックボックスが {2} に切り替えられました",
                "korean": "게시물 {0} (ID: {1})의 체크박스가 {2}(으)로 전환되었습니다",
                "chinese-simplified": "帖子 {0} (ID: {1}) 的复选框已切换为 {2}"
            },
            
            "check_all_state_updated": {
                "english": "Check ALL state updated to {0}",
                "japanese": "すべてをチェック状態が {0} に更新されました",
                "korean": "모두 선택 상태가 {0}(으)로 업데이트되었습니다",
                "chinese-simplified": "全选状态已更新为 {0}"
            },
            
            "viewing_not_supported_for_url": {
                "english": "Viewing not supported for {0}",
                "japanese": "{0} の表示はサポートされていません",
                "korean": "{0} 보기 기능은 지원되지 않습니다",
                "chinese-simplified": "不支持查看 {0}"
            },
            
            "starting_cancellation_of_active_threads": {
                "english": "Starting cancellation of active threads",
                "japanese": "アクティブスレッドのキャンセルを開始します",
                "korean": "활성 스레드 취소를 시작합니다",
                "chinese-simplified": "开始取消活动线程"
            },
            "signaled_stop_for_thread": {
                "english": "Signaled stop for thread {0}",
                "japanese": "スレッド {0} に停止シグナルを送信しました",
                "korean": "스레드 {0}에 정지 신호를 보냈습니다",
                "chinese-simplified": "已向线程 {0} 发送停止信号"
            },
            "thread_already_deleted": {
                "english": "Thread {0} already deleted",
                "japanese": "スレッド {0} はすでに削除されています",
                "korean": "스레드 {0} 는 이미 삭제되었습니다",
                "chinese-simplified": "线程 {0} 已被删除"
            },
            
            "checkbox_toggle_completed": {
                "english": "Checkbox toggle completed: Check ALL = {0}, Affected posts: {1}, Total checked: {2}",
                "japanese": "チェックボックスの切り替えが完了しました：すべてチェック = {0}、影響を受けた投稿：{1}、合計チェック数：{2}",
                "korean": "체크박스 토글 완료: 모두 체크 = {0}, 영향을 받은 게시물: {1}, 총 체크 수: {2}",
                "chinese-simplified": "复选框切换完成：全部选中 = {0}，受影响的帖子：{1}，总计选中：{2}"
            },
            
            "invalid_url_type": {
                "english": "Invalid URL type: {0}. Expected string.",
                "japanese": "無効なURLタイプ：{0}。文字列が必要です。",
                "korean": "잘못된 URL 유형: {0}. 문자열이 필요합니다.",
                "chinese-simplified": "无效的URL类型：{0}。需要字符串。"
            },
            
            "post_detection_in_progress": {
                "english": "Post detection already in progress. Please wait.",
                "japanese": "投稿検出がすでに進行中です。しばらくお待ちください。",
                "korean": "게시물 감지가 이미 진행 중입니다. 잠시 기다려 주세요。",
                "chinese-simplified": "帖子检测已在进行中。请稍等。"
            },
            
            "populated_posts_for_creator": {
                "english": "Populated {0} posts for creator {1}",
                "japanese": "クリエイター {1} のために {0} 件の投稿を入力しました",
                "korean": "크리에이터 {1}을 위해 {0}개의 게시물을 채웠습니다",
                "chinese-simplified": "为创建者 {1} 填充了 {0} 个帖子"
            },
            
            "no_creator_viewed": {
                "english": "No creator currently viewed to download.",
                "japanese": "現在ダウンロードするクリエイターが表示されていません。",
                "korean": "현재 다운로드할 크리에이터가 없습니다.",
                "chinese-simplified": "当前没有查看的创建者可供下载。"
            },
            
            "posts_to_download_num": {
                "english": "Posts to download: {0}",
                "japanese": "ダウンロードする投稿数：{0}",
                "korean": "다운로드할 게시물 수: {0}",
                "chinese-simplified": "要下载的帖子数：{0}"
            },
            
            "file_preparation_in_progress": {
                "english": "File preparation already in progress. Please wait.",
                "japanese": "ファイルの準備がすでに進行中です。しばらくお待ちください。",
                "korean": "파일 준비가 이미 진행 중입니다. 잠시 기다려 주세요。",
                "chinese-simplified": "文件准备已在进行中。请稍等。"
            },
            
            "post_id_mismatch": {
                "english": "Post ID mismatch: Expected {0}, got {1}",
                "japanese": "投稿IDの不一致：期待値 {0}、取得値 {1}",
                "korean": "게시물 ID 불일치: 기대값 {0}, 실제값 {1}",
                "chinese-simplified": "帖子ID不匹配：预期 {0}，实际 {1}"
            },
            
            "no_posts_available": {
                "english": "No posts available for download. Skipping.",
                "japanese": "ダウンロード可能な投稿がありません。スキップします。",
                "korean": "다운로드할 수 있는 게시물이 없습니다. 건너뜁니다.",
                "chinese-simplified": "没有可下载的帖子。跳过。"
            },
            
            "detected_file": {
                "english": "Detected file: {0} from {1}",
                "japanese": "検出されたファイル：{0}（{1} から）",
                "korean": "감지된 파일: {0} ({1}에서)",
                "chinese-simplified": "检测到的文件：{0}（来自 {1}）"
            },
            
            "no_files_detected": {
                "english": "No files detected for selected posts. Skipping.",
                "japanese": "選択した投稿にファイルが検出されませんでした。スキップします。",
                "korean": "선택한 게시물에 파일이 감지되지 않았습니다. 건너뜁니다。",
                "chinese-simplified": "未检测到所选帖子的文件。跳过。"
            },
            
            "prepared_files_for_download": {
                "english": "Prepared {0} files for download",
                "japanese": "{0} 件のファイルをダウンロード用に準備しました",
                "korean": "{0}개의 파일을 다운로드 준비했습니다",
                "chinese-simplified": "为下载准备了 {0} 个文件"
            },
            
            "file_completed": {
                "english": "File completed: {0}, Total completed: {1}/{2}",
                "japanese": "ファイル完了: {0}, 完了合計: {1}/{2}",
                "korean": "파일 완료: {0}, 총 완료: {1}/{2}",
                "chinese-simplified": "文件完成：{0}, 已完成总数：{1}/{2}"
            },
            "file_failed": {
                "english": "File failed: {0}, Total failed: {1}",
                "japanese": "ファイル失敗: {0}, 失敗合計: {1}",
                "korean": "파일 실패: {0}, 총 실패: {1}",
                "chinese-simplified": "文件失败：{0}, 失败总数：{1}"
            },
            "all_files_attempted": {
                "english": "All files attempted (successful or failed), triggering download finished",
                "japanese": "すべてのファイルを試行しました（成功または失敗）、ダウンロード完了をトリガーします",
                "korean": "모든 파일을 시도했습니다(성공 또는 실패), 다운로드 완료를 트리거합니다",
                "chinese-simplified": "所有文件已尝试（成功或失败），触发下载完成"
            },
            
            "moving_to_next_creator": {
                "english": "Moving to next creator: {0}",
                "japanese": "次のクリエイターに移ります：{0}",
                "korean": "다음 크리에이터로 이동: {0}",
                "chinese-simplified": "移动到下一个创建者：{0}"
            },
            
            "terminated_lingering_thread": {
                "english": "Terminated lingering thread: {0}",
                "japanese": "残留スレッドを終了しました：{0}",
                "korean": "잔류 스레드를 종료했습니다: {0}",
                "chinese-simplified": "终止了残留线程：{0}"
            },
            
            "waiting_for_remaining_files": {
                "english": "Waiting for remaining files: {0}/{1}, Failed: {2}, Active threads: {3}",
                "japanese": "残りのファイルを待機中: {0}/{1}, 失敗: {2}, アクティブスレッド: {3}",
                "korean": "남은 파일을 기다리는 중: {0}/{1}, 실패: {2}, 활성 스레드: {3}",
                "chinese-simplified": "正在等待剩余文件：{0}/{1}, 失败：{2}, 活动线程：{3}"
            },
            
            "no_active_downloads_to_cancel": {
                "english": "No active downloads to cancel",
                "japanese": "キャンセルするアクティブなダウンロードはありません",
                "korean": "취소할 활성 다운로드가 없습니다",
                "chinese-simplified": "没有可取消的活动下载"
            },
            
            "deleting_thread": {
                "english": "Deleting thread {0}",
                "japanese": "スレッド {0} を削除中",
                "korean": "스레드 {0} 삭제 중",
                "chinese-simplified": "正在删除线程 {0}"
            },
            
            "no_more_active_threads": {
                "english": "No more active threads or creators. Finishing.",
                "japanese": "これ以上アクティブなスレッドや作成者はありません。終了します。",
                "korean": "더 이상 활성 스레드나 생성자가 없습니다. 종료합니다.",
                "chinese-simplified": "没有更多活动的线程或创建者。正在结束。"
            },
            
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
            "size_mismatch_error": {
                "english": "Downloaded size ({0} bytes) does not match expected size ({1} bytes) for {2}",
                "japanese": "ダウンロードサイズ（{0}バイト）が予期されるサイズ（{1}バイト）と一致しません：{2}",
                "korean": "다운로드된 크기({0}바이트)가 예상 크기({1}바이트)와 일치하지 않습니다: {2}",
                "chinese-simplified": "下载大小（{0}字节）与预期大小（{1}字节）不匹配：{2}"
            },
            "deleted_incomplete_file": {
                "english": "Deleted incomplete file: {0}",
                "japanese": "不完全なファイルを削除しました：{0}",
                "korean": "불완전한 파일 삭제됨: {0}",
                "chinese-simplified": "已删除不完整的文件：{0}"
            },
            "failed_to_delete_incomplete_file": {
                "english": "Failed to delete incomplete file {0}: {1}",
                "japanese": "不完全なファイル{0}の削除に失敗しました：{1}",
                "korean": "불완전한 파일 {0} 삭제 실패: {1}",
                "chinese-simplified": "删除不完整的文件 {0} 失败：{1}"
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
                "english": "Check ALL (Page)",
                "japanese": "すべてチェック (ページ)",
                "korean": "모두 선택 (페이지)",
                "chinese-simplified": "全选 (页面)"
            },
            "check_all_all": {
                "english": "Check ALL (All)",
                "japanese": "すべてチェック (すべて)",
                "korean": "모두 선택 (모두)",
                "chinese-simplified": "全选 (全部)"
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
            "page_info": {
                "english": "Page {0} of {1}",
                "japanese": "ページ {0} / {1}",
                "korean": "페이지 {0} / {1}",
                "chinese-simplified": "第 {0} 页，共 {1} 页"
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
            "retry_settings": {
                "english": "Retry Settings",
                "japanese": "リトライ設定",
                "korean": "재시도 설정",
                "chinese-simplified": "重试设置"
            },
            "creator_posts_max_attempts": {
                "english": "Creator Posts Max Attempts:",
                "japanese": "クリエイター投稿最大試行回数:",
                "korean": "크리에이터 게시물 최대 시도 횟수:",
                "chinese-simplified": "创作者帖子最大尝试次数:"
            },
            "post_data_max_retries": {
                "english": "Post Data Max Retries:",
                "japanese": "投稿データ最大リトライ回数:",
                "korean": "게시물 데이터 최대 재시도 횟수:",
                "chinese-simplified": "帖子数据最大重试次数:"
            },
            "file_download_max_retries": {
                "english": "File Download Max Retries:",
                "japanese": "ファイルダウンロード最大リトライ回数:",
                "korean": "파일 다운로드 최대 재시도 횟수:",
                "chinese-simplified": "文件下载最大重试次数:"
            },
            "api_request_max_retries": {
                "english": "API Request Max Retries:",
                "japanese": "APIリクエスト最大リトライ回数:",
                "korean": "API 요청 최대 재시도 횟수:",
                "chinese-simplified": "API请求最大重试次数:"
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
            
            "remove_thread": {
                "english": "Removed thread {0} from active threads",
                "japanese": "アクティブなスレッドからスレッド {0} を削除しました",
                "korean": "활성 스레드에서 스레드 {0}을 제거했습니다",
                "chinese-simplified": "从活跃线程中移除线程 {0}"
            },
            
            "transferred_from": {
                "english": "Transferred {0} from {1}",
                "japanese": "{1} から {0} を転送しました",
                "korean": "{1}에서 {0}을(를) 전송했습니다",
                "chinese-simplified": "从 {1} 转移了 {0}"
            },
            
            "all_files_attempted_for_creator": {
                "english": "All files attempted for current creator. Finalizing.",
                "japanese": "現在のクリエイターのすべてのファイルの試行が完了しました。最終処理中。",
                "korean": "현재 크리에이터의 모든 파일 시도가 완료되었습니다. 마무리 중입니다.",
                "chinese-simplified": "当前创建者的所有文件尝试已完成。正在完成。"
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
            "refetching_posts_for_creator": {
                "english": "Refetching posts for creator: {0}",
                "japanese": "クリエイターの投稿を再取得中: {0}",
                "korean": "크리에이터의 게시물 다시 가져오는 중: {0}",
                "chinese-simplified": "重新获取创作者的投稿: {0}"
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
            "cancelling_post_detection": {
                "english": "Cancelling post detection...",
                "japanese": "投稿検出をキャンセル中...",
                "korean": "게시물 감지 취소 중...",
                "chinese-simplified": "正在取消投稿检测..."
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
            
            "invalid_url_format_link": {
                "english": "Invalid URL format: {0}",
                "japanese": "無効なURL形式：{0}",
                "korean": "잘못된 URL 형식: {0}",
                "chinese-simplified": "无效的URL格式：{0}"
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
                          "아래 섹션을 따라 케모노 다운로더의 각 탭과 기능을 사용하는 방법을 알아보세요.",
                "chinese-simplified": "欢迎使用 Kemono 下载器，这是一款功能强大的工具，旨在帮助您从 Kemono.cr 下载内容，这是一个归档 Patreon、Fanbox 等多种创作者服务帖子的平台。本用户手册提供了详细的使用说明，深入涵盖应用程序的每个功能和选项卡。无论您是下载单个帖子还是整个创作者的归档，本指南都将引导您完成每个步骤，解释界面，并提供故障排除提示，以确保顺畅的使用体验。<br><br>"
                           "<b>主要功能：</b><br>"
                           "- 从 Kemono.cr 下载单个帖子或整个创作者资料。<br>"
                           "- 支持多种文件类型，包括图片（JPG、PNG、GIF）、视频（MP4）、归档文件（ZIP、7Z）和 PDF。<br>"
                           "- 支持并发下载以提高性能，并提供可自定义的设置。<br>"
                           "- 下载前预览图片以确认内容。<br>"
                           "- 使用 URL 哈希进行文件去重，避免重复下载。<br>"
                           "- 提供详细日志，用于监控下载进度和诊断问题。<br>"
                           "- 可自定义保存目录、主题和通知设置。<br><br>"
                           "请按照以下章节学习如何使用 Kemono 下载器的每个选项卡和功能。"
                
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
                          "- 애플리케이션이 Kemono.su에서 데이터를 가져와야 하므로 활성 인터넷 연결을 확인하세요.",
                "chinese-simplified": "<b>1.1 启动应用程序</b><br>"
                           "- 首次打开 Kemono 下载器时，您将看到一个包含应用程序标题“Kemono.cr 下载器”的介绍屏幕。<br>"
                           "- 标题下方显示开发者的名称（“Developed by VoxDroid”）以及指向 GitHub 仓库（github.com/VoxDroid）的可点击链接，以获取更新和支持。<br>"
                           "- 点击屏幕中央的“启动”按钮进入主界面。<br><br>"
                           "<b>1.2 主界面概览</b><br>"
                           "主界面分为四个选项卡，每个选项卡都有特定用途：<br>"
                           "  - <b>帖子下载器</b>：使用此选项卡通过输入 URL 下载特定 Kemono.cr 帖子的文件。适合下载单个帖子。<br>"
                           "  - <b>创作者下载器</b>：使用此选项卡下载整个创作者资料的内容，获取所有帖子及相关文件。<br>"
                           "  - <b>设置</b>：配置应用程序的行为，例如保存目录、同时下载数量和界面偏好设置。<br>"
                           "  - <b>帮助</b>：您现在所在的位置！此选项卡提供全面的用户手册，指导您使用应用程序。<br><br>"
                           "<b>1.3 界面元素</b><br>"
                           "- <b>选项卡</b>：位于主界面顶部，带有图标和标签样式。当前激活的选项卡会以较深的背景高亮显示。<br>"
                           "- <b>状态栏</b>：位于窗口底部，状态标签（例如“空闲”）显示应用程序的当前状态。在下载等操作期间会更新。<br>"
                           "- <b>页脚</b>：同样位于底部，显示开发者名称和 GitHub 链接，便于快速访问项目页面。<br><br>"
                           "<b>1.4 初始设置</b><br>"
                           "- 首次启动时，应用程序会在默认保存位置（可在设置选项卡中配置）创建以下目录：<br>"
                           "  - <b>下载</b>：保存下载文件的目录。<br>"
                           "  - <b>缓存</b>：存储用于图片预览的临时文件。<br>"
                           "  - <b>其他文件</b>：包含用于去重的文件哈希等元数据。<br>"
                           "- 确保您的网络连接正常，因为应用程序需要从 Kemono.cr 获取数据。"
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
                          "- <b>로깅</b>: 콘솔은 파일 감지, 다운로드 진행 상황, 오류를 포함한 모든 작업에 대한 자세한 로그를 제공하여 문제 디버깅에 유용합니다.",
                "chinese-simplified": "帖子下载器选项卡专为从特定 Kemono.cr 帖子下载内容而设计。您可以将多个帖子添加到队列，查看其内容，选择要下载的文件，并监控下载进度。以下是有效使用此选项卡的详细步骤：<br><br>"
                           "<b>2.1 将帖子添加到队列</b><br>"
                           "- <b>步骤 1</b>：点击界面顶部的“帖子下载器”标签进入该选项卡。该选项卡标有下载图标。<br>"
                           "- <b>步骤 2</b>：找到选项卡左上方的“输入帖子 URL”字段。这是一个带有占位符文本“输入帖子 URL（例如：https://kemono.cr/patreon/user/123/post/456）”的文本输入框。<br>"
                           "- <b>步骤 3</b>：输入 Kemono.cr 帖子的 URL。URL 必须遵循以下格式：https://kemono.cr/[service]/user/[user_id]/post/[post_id]。例如：https://kemono.cr/patreon/user/123456785/post/12345678。<br>"
                           "- <b>步骤 4</b>：点击输入字段旁边的“添加到队列”按钮。该按钮带有加号图标和蓝色背景。<br>"
                           "- <b>步骤 5</b>：帖子 URL 将显示在输入字段下方的“帖子队列”列表中。列表中的每个条目包括：<br>"
                           "  - 一个用于查看帖子内容的眼睛图标。<br>"
                           "  - 作为可点击标签的帖子 URL。<br>"
                           "  - 一个用于从队列中删除帖子的“X”按钮。<br><br>"
                           "<b>2.2 查看帖子内容</b><br>"
                           "- <b>步骤 1</b>：在“帖子队列”列表中，找到您想要检查的帖子。<br>"
                           "- <b>步骤 2</b>：点击帖子 URL 旁边的眼睛图标。这将启动一个后台任务，从 Kemono.cr 获取帖子数据。<br>"
                           "- <b>步骤 3</b>：与帖子相关的文件将显示在选项卡右侧的“待下载文件”列表中。<br>"
                           "- <b>步骤 4</b>：使用“按类型过滤”复选框（例如：JPG、ZIP、MP4）仅显示特定文件类型。例如，勾选“JPG”将仅显示扩展名为 .jpg 或 .jpeg 的图片文件。<br>"
                           "- <b>步骤 5</b>：使用“待下载文件”列表上方的搜索栏按文件名过滤文件。例如，输入“image”将仅显示文件名中包含“image”的文件。<br>"
                           "- <b>注意</b>：在获取帖子数据时，右下方的“后台任务进度”条将显示循环动画，其上方标签将显示“正在从链接获取文件...”。<br><br>"
                           "<b>2.3 选择要下载的文件</b><br>"
                           "- <b>步骤 1</b>：在“待下载文件”列表中，每个文件旁都有一个复选框。默认情况下，所有文件都被选中（复选框已勾选）。<br>"
                           "- <b>步骤 2</b>：取消勾选您不想下载的文件的复选框。例如，如果您只想要图片，请取消 ZIP 或 MP4 文件的勾选。<br>"
                           "- <b>步骤 3</b>：使用列表上方的“全选”复选框快速选择或取消选择所有可见文件。如果应用了过滤器，这仅影响过滤后的文件。<br>"
                           "- <b>步骤 4</b>：要一次性下载队列中所有帖子的文件，请勾选“下载所有链接”选项。这将禁用单个文件选择，并准备下载队列中所有帖子的所有文件。<br>"
                           "- <b>注意</b>：当启用“下载所有链接”时，“待下载文件”列表中的复选框将被禁用，应用程序将尝试下载队列中所有帖子的所有文件。<br><br>"
                           "<b>2.4 开始下载</b><br>"
                           "- <b>步骤 1</b>：确保已选择所需文件或启用了“下载所有链接”。<br>"
                           "- <b>步骤 2</b>：点击选项卡左下方的“下载”按钮。该按钮标有下载图标并带有蓝色背景。<br>"
                           "- <b>步骤 3</b>：下载过程将开始，以下元素将更新：<br>"
                           "  - <b>文件进度条</b>：显示当前下载文件的进度（0% 到 100%）。其上方的标签（例如“文件进度 50%”）会相应更新。<br>"
                           "  - <b>总进度条</b>：显示所有文件和帖子的总体进度（例如“总进度（5/10 文件，2/3 帖子）”）。<br>"
                           "  - <b>控制台</b>：记录下载过程的消息，例如“开始下载文件 1/10：[URL]”或“成功下载：[路径]”。日志采用颜色编码：绿色表示信息，黄色表示警告，红色表示错误。<br>"
                           "- <b>注意</b>：下载期间，“下载”按钮将禁用，“取消”按钮将启用。<br><br>"
                           "<b>2.5 管理下载</b><br>"
                           "- <b>取消下载</b>：点击“取消”按钮（标有“X”图标）停止所有活动下载。进度条将变为黄色，标签将更新为“下载已终止”。<br>"
                           "- <b>从队列中删除帖子</b>：点击“帖子队列”列表中帖子 URL 旁边的“X”按钮删除帖子。您将被提示确认删除。<br>"
                           "- <b>预览图片</b>：在“待下载文件”列表中选择图片文件（JPG、JPEG、PNG 或 GIF），然后点击列表下方的眼睛图标按钮进行预览。将打开一个显示图片的模态窗口，加载时显示进度条。<br>"
                           "- <b>注意</b>：如果在活动下载期间删除了帖子，该帖子的文件下载将被取消。<br><br>"
                           "<b>2.6 文件保存位置</b><br>"
                           "- 文件将保存在设置选项卡中指定的目录中（默认为用户目录下的“Kemono Downloader/Downloads”）。<br>"
                           "- 文件夹结构组织如下：<br>"
                           "  - <b>服务文件夹</b>：以服务命名（例如“patreon”）。<br>"
                           "  - <b>帖子文件夹</b>：命名为“post_[post_id]”（例如“post_12345678”）。<br>"
                           "  - 示例：从 https://kemono.cr/patreon/user/123456785/post/12345678 下载的文件将保存在“[保存目录]/patreon/post_12345678/”中。<br>"
                           "- 文件名基于其原始 URL，任何特殊字符（例如“/”）都将替换为下划线，以确保与文件系统的兼容性。<br><br>"
                           "<b>2.7 附加功能</b><br>"
                           "- <b>并发下载</b>：应用程序支持同时下载多个文件，并发下载数量在设置选项卡中设置（默认为 10，可在 1-10 之间调整）。<br>"
                           "- <b>文件去重</b>：应用程序使用 URL 哈希检测并跳过之前下载的文件，防止重复。哈希数据存储在“其他文件”目录中的“file_hashes.json”中。<br>"
                           "- <b>图片缓存</b>：预览图片时，图片会缓存到“缓存”目录中，以加快相同图片的未来预览速度。<br>"
                           "- <b>日志记录</b>：控制台提供所有操作的详细日志，包括文件检测、下载进度和错误。这对于调试问题非常有用。"
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
                          "- <b>배치 처리</b>: '모든 링크 다운로드'가 활성화되면 애플리케이션은 자원을 효율적으로 관리하기 위해 각 크리에이터를 순차적으로 처리하며, 한 번에 한 크리에이터의 파일을 준비하고 다운로드합니다.",
                "chinese-simplified": "创作者下载器选项卡专为从 Kemono.cr 上某个创作者的整个资料批量下载内容而设计。您可以将多个创作者添加到队列，获取他们的帖子，选择特定内容进行下载，并监控进度。此选项卡非常适合归档创作者的作品或一次下载多个创作者的内容。以下是有效使用此选项卡的详细步骤：<br><br>"
                           "<b>3.1 将创作者添加到队列</b><br>"
                           "- <b>步骤 1</b>：点击界面顶部的“创作者下载器”标签进入该选项卡。该选项卡标有用户编辑图标。<br>"
                           "- <b>步骤 2</b>：找到选项卡左上方的“输入创作者 URL”字段。这是一个带有占位符文本“输入创作者 URL（例如：https://kemono.cr/patreon/user/12345678）”的文本输入框。<br>"
                           "- <b>步骤 3</b>：输入 Kemono.cr 上创作者资料的 URL。URL 必须遵循以下格式：https://kemono.cr/[service]/user/[user_id]。例如：https://kemono.cr/patreon/user/12345678。<br>"
                           "- <b>步骤 4</b>：点击输入字段旁边的“添加到队列”按钮。该按钮带有加号图标和蓝色背景。<br>"
                           "- <b>步骤 5</b>：创作者 URL 将显示在输入字段下方的“创作者队列”列表中。列表中的每个条目包括：<br>"
                           "  - 一个用于获取和查看创作者帖子的眼睛图标。<br>"
                           "  - 作为可点击标签的创作者 URL。<br>"
                           "  - 一个用于从队列中删除创作者的“X”按钮。<br>"
                           "- <b>注意</b>：系统会自动防止重复的 URL。如果您尝试添加已在队列中的 URL，控制台将显示警告消息：“[警告] URL 已在队列中。”<br><br>"
                           "<b>3.2 查看创作者帖子</b><br>"
                           "- <b>步骤 1</b>：在“创作者队列”列表中，找到您想要查看帖子的创作者。<br>"
                           "- <b>步骤 2</b>：点击创作者 URL 旁边的眼睛图标。这将启动一个后台任务，从 Kemono.cr 获取与该创作者相关的所有帖子。<br>"
                           "- <b>步骤 3</b>：帖子将显示在选项卡右侧的“待下载帖子”列表中。每个帖子条目包括：<br>"
                           "  - 用于选择下载帖子的复选框。<br>"
                           "  - 帖子标题（如果没有标题，则显示为“帖子 [post_id]”）。<br>"
                           "  - 作为用户数据存储的缩略图 URL（如果可用）用于预览。<br>"
                           "- <b>步骤 4</b>：使用“待下载帖子”列表上方的搜索栏按标题过滤帖子。例如，输入“artwork”将仅显示标题中包含“artwork”的帖子。<br>"
                           "- <b>注意</b>：在获取帖子时，右下方的“后台任务进度”条将显示循环动画，其标签显示“正在从链接检测帖子...”。完成后，标签将变为“空闲”。<br><br>"
                           "<b>3.3 配置下载选项</b><br>"
                           "- <b>步骤 1</b>：在“下载选项”分组框中，配置要包含的下载内容类型：<br>"
                           "  - <b>主要文件</b>：包括每个帖子的主要文件（例如特色图片或视频）。默认启用。<br>"
                           "  - <b>附件</b>：包括帖子附加的其他文件（例如 ZIP 文件、额外图片）。默认启用。<br>"
                           "  - <b>内容图片</b>：包括帖子内容中嵌入的图片（例如帖子描述中的图片）。默认启用。<br>"
                           "- <b>步骤 2</b>：在“文件扩展名”分组框中，选择要下载的文件类型：<br>"
                           "  - 选项包括 JPG/JPEG、PNG、ZIP、MP4、GIF、PDF 和 7Z。<br>"
                           "  - 所有文件类型默认启用。取消勾选您不想下载的文件类型。<br>"
                           "  - 示例：如果您只想要图片，请取消 ZIP、MP4、PDF 和 7Z 的勾选，仅保留 JPG/JPEG、PNG 和 GIF。<br>"
                           "- <b>注意</b>：更改这些选项将会在开始下载过程时自动更新待下载文件列表。<br><br>"
                           "<b>3.4 选择要下载的帖子</b><br>"
                           "- <b>步骤 1</b>：在“待下载帖子”列表中，勾选您想要下载的帖子旁边的复选框。默认情况下没有帖子被选中。<br>"
                           "- <b>步骤 2</b>：使用列表上方的“全选”复选框快速选择或取消选择所有可见帖子。如果应用了搜索过滤器，这仅影响过滤后的帖子。<br>"
                           "- <b>步骤 3</b>：或者，启用“下载所有链接”选项，无需手动选择即可下载队列中所有创作者的所有文件：<br>"
                           "  - 启用后，此选项将禁用单个帖子复选框，并获取队列中所有创作者的所有帖子。<br>"
                           "  - 应用程序将自动选择所有帖子进行下载，忽略手动选择。<br>"
                           "- <b>注意</b>：列表下方的“帖子：[数量]”标签会更新以反映所选帖子的数量。启用“下载所有链接”时，它显示队列中所有创作者的帖子总数。<br><br>"
                           "<b>3.5 开始下载</b><br>"
                           "- <b>步骤 1</b>：确保已选择所需帖子或启用了“下载所有链接”。<br>"
                           "- <b>步骤 2</b>：点击选项卡左下方的“下载”按钮。该按钮标有下载图标并带有蓝色背景。<br>"
                           "- <b>步骤 3</b>：应用程序将首先准备下载文件，在后台任务标签中显示“正在准备下载文件...”并显示进度条。<br>"
                           "- <b>步骤 4</b>：准备完成后，下载过程开始，以下元素将更新：<br>"
                           "  - <b>文件进度条</b>：显示当前下载文件的进度（0% 到 100%）。其上方的标签（例如“文件进度 50%”）会相应更新。<br>"
                           "  - <b>总进度条</b>：显示所有文件和帖子的总体进度（例如“总进度（5/10 文件，2/3 帖子）”）。<br>"
                           "  - <b>控制台</b>：记录消息，例如“开始下载文件 1/10：[URL]”或“成功下载：[路径]”。日志采用颜色编码：绿色表示信息，黄色表示警告，红色表示错误。<br>"
                           "- <b>注意</b>：下载期间，“下载”按钮将禁用，“取消”按钮将启用，“帖子下载器”选项卡将暂时禁用以防止冲突。<br><br>"
                           "<b>3.6 管理下载</b><br>"
                           "- <b>取消下载</b>：点击“取消”按钮（标有“X”图标）停止所有活动下载。进度条将变为黄色，标签将更新为“下载已终止”。“帖子下载器”选项卡将重新启用。<br>"
                           "- <b>从队列中删除创作者</b>：点击“创作者队列”列表中创作者 URL 旁边的“X”按钮删除。您将被提示确认删除。如果在活动下载期间删除，该创作者的帖子下载将被取消。<br>"
                           "- <b>预览图片</b>：在“待下载帖子”列表中选择帖子，然后点击列表下方的眼睛图标按钮预览其缩略图（如果可用）。仅支持 JPG、JPEG、PNG 和 GIF 文件的预览。将打开一个显示图片的模态窗口，加载时显示进度条。<br>"
                           "- <b>注意</b>：如果点击“下载”时未选择任何帖子，控制台将显示警告：“[警告] 未选择要下载的帖子。”<br><br>"
                           "<b>3.7 文件保存位置</b><br>"
                           "- 文件将保存在设置选项卡中指定的目录中（默认为用户目录下的“Kemono Downloader/Downloads”）。<br>"
                           "- 文件夹结构组织如下：<br>"
                           "  - <b>创作者文件夹</b>：以创作者的 ID 命名（例如“12345678”）。<br>"
                           "  - <b>帖子文件夹</b>：在创作者文件夹内命名为“post_[post_id]”（例如“post_12345678”）。<br>"
                           "  - 示例：从创作者 https://kemono.cr/patreon/user/12345678 下载的帖子 12345678 的文件将保存在“[保存目录]/12345678/post_12345678/”中。<br>"
                           "- 文件名基于其原始 URL，任何特殊字符（例如“/”）都将替换为下划线，以确保与文件系统的兼容性。<br>"
                           "- <b>文件去重</b>：应用程序使用 URL 哈希检测并跳过之前下载的文件，哈希数据存储在“其他文件”目录中的“file_hashes.json”中。<br><br>"
                           "<b>3.8 附加功能</b><br>"
                           "- <b>并发下载</b>：应用程序支持同时下载多个文件，并发下载数量在设置选项卡中设置（默认为 10，可在 1-10 之间调整）。<br>"
                           "- <b>图片缓存</b>：缩略图和预览图片缓存到“缓存”目录中，以加快相同图片的未来预览速度。<br>"
                           "- <b>日志记录</b>：控制台提供所有操作的详细日志，包括帖子检测、文件准备、下载进度和错误。这对于调试问题非常有用。<br>"
                           "- <b>批量处理</b>：启用“下载所有链接”时，应用程序按顺序处理创作者，逐一准备和下载每个创作者的文件，以有效管理资源。"
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
                          "- '로깅 활성화'를 비활성화하면 콘솔에 치명적인 오류만 표시되며, 일상적인 정보와 경고는 숨겨집니다.",
                "chinese-simplified": "设置选项卡允许您自定义 Kemono 下载器的行为和外观，以满足您的偏好。从更改保存目录到调整同时下载数量，此选项卡提供了优化使用体验所需的所有工具。以下是此选项卡中可用的详细选项：<br><br>"
                           "<b>4.1 常规设置</b><br>"
                           "- <b>保存目录</b>：指定下载文件的保存位置。<br>"
                           "  - 默认：用户目录下的“Kemono Downloader/Downloads”。<br>"
                           "  - 点击文本字段旁边的“浏览”按钮，打开文件对话框并选择新目录。<br>"
                           "  - 示例：将其更改为“D:/Kemono Downloads”，文件将保存到该目录。<br>"
                           "- <b>最大同时下载数</b>：控制一次下载的文件数量。<br>"
                           "  - 默认：10。<br>"
                           "  - 使用旋转框在 1 到 10 之间调整。较低的值会减少带宽使用但会减慢进程；较高的值会加快速度但可能对网络连接造成压力。<br><br>"
                           "<b>4.2 保存更改</b><br>"
                           "- 对“保存目录”、“最大同时下载数”和“语言”等设置的更改在调整时会自动保存。<br>"
                           "- “清除缓存”和“重置文件哈希”等操作需要通过相应按钮手动确认。<br>"
                           "- 没有“保存”按钮；所有设置除非手动重置（例如通过“重置哈希”），否则会在会话间持久保存。<br><br>"
                           "<b>4.3 注意事项</b><br>"
                           "- 更改“保存目录”仅影响新下载；现有文件将保留在原始位置。<br>"
                           "- 在活动下载期间调整“最大同时下载数”不会影响当前会话，但会应用于下一个会话。<br>"
                           "- 如果禁用“启用日志”，控制台仍会显示严重错误，但常规信息和警告将被隐藏。"
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
                          "- 여기서 다루지 않은 문제에 직면하면 '문제 해결' 또는 '연락 및 지원' 섹션을 참조하여 추가 도움을 받으세요.",
                "chinese-simplified": "帮助选项卡为 Kemono 下载器提供了全面的用户手册，指导您了解应用程序的每个方面。无论您是新用户还是需要复习，此选项卡是您了解如何有效使用该工具的主要资源。<br><br>"
                           "<b>5.1 访问帮助选项卡</b><br>"
                           "- 点击界面顶部的“帮助”标签进入该选项卡。该选项卡标有问号图标。<br>"
                           "- 内容显示在可滚动区域中，背景为深蓝色灰色（#2A3B5A），与默认主题相匹配。<br><br>"
                           "<b>5.2 内容概览</b><br>"
                           "- <b>简介</b>：欢迎消息和应用程序主要功能的概述。<br>"
                           "- <b>开始使用</b>：启动应用程序和了解主界面的说明。<br>"
                           "- <b>帖子下载器选项卡</b>：从特定帖子下载内容的详细步骤。<br>"
                           "- <b>创作者下载器选项卡</b>：从创作者资料批量下载的说明。<br>"
                           "- <b>设置选项卡</b>：所有可自定义选项的说明。<br>"
                           "- <b>帮助选项卡</b>：本节，描述帮助选项卡的目的和结构。<br>"
                           "- <b>故障排除</b>：常见问题及其解决方法。<br>"
                           "- <b>联系与支持</b>：获取帮助或报告问题的信息。<br><br>"
                           "<b>5.3 使用帮助选项卡</b><br>"
                           "- 使用选项卡右侧的垂直滚动条浏览各个部分。<br>"
                           "- 每个部分都以白色文本的粗体标题（例如“1. 开始使用”）清晰标注，后面跟着浅灰色（#D0D0D0）的详细说明。<br>"
                           "- 文本使用 HTML 标签（例如，<b> 表示粗体）格式化，以突出重要内容。<br>"
                           "- 内容会根据设置选项卡中选择的语言（英语、日语或韩语）动态更新。<br><br>"
                           "<b>5.4 注意事项</b><br>"
                           "- 帮助选项卡是静态的，所有内容都嵌入在应用程序中，因此查看时无需互联网连接。<br>"
                           "- 如果遇到本文未涵盖的问题，请参阅“故障排除”或“联系与支持”部分以获取进一步帮助。"
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
                          "- <b>해결책</b>: 설정 탭에서 새 언어를 선택한 후 변경이 즉시 적용되지 않으면 애플리케이션을 재시작하세요.",
                "chinese-simplified": "本节解决您在使用 Kemono 下载器时可能遇到的常见问题，并提供相应的解决方案。如果您的问题未在此列出，请参阅“联系与支持”部分以获取进一步帮助。<br><br>"
                           "<b>6.1 下载失败并显示“连接错误”</b><br>"
                           "- <b>原因</b>：无互联网连接或 Kemono.cr 暂时不可用。<br>"
                           "- <b>解决方案</b>：检查您的互联网连接。等待几分钟后重试，因为网站可能正在维护。检查控制台中的具体错误消息（例如“[错误] 无法连接到 URL”）。<br><br>"
                           "<b>6.2 文件未下载</b><br>"
                           "- <b>原因</b>：未选择文件，或帖子/创作者 URL 无效。<br>"
                           "- <b>解决方案</b>：确保在“待下载文件”或“待下载帖子”列表中选择了文件或帖子。验证 URL 格式（例如 https://kemono.cr/patreon/user/12345678/post/12345678）。检查控制台中的警告，例如“[警告] 未找到 URL 的文件”。<br><br>"
                           "<b>6.3 下载速度慢</b><br>"
                           "- <b>原因</b>：同时下载过多或互联网连接缓慢。<br>"
                           "- <b>解决方案</b>：在设置选项卡中减少“最大同时下载数”（例如从 10 减少到 5）。测试您的互联网速度，确保这不是瓶颈。<br><br>"
                           "<b>6.4 图片预览无法加载</b><br>"
                           "- <b>原因</b>：缓存损坏或网络问题。<br>"
                           "- <b>解决方案</b>：转到设置选项卡，点击“清除缓存”删除临时文件。再次尝试预览。如果问题持续，检查您的互联网连接或 Kemono.cr 上文件的可用性。<br><br>"
                           "<b>6.5 下载了重复文件</b><br>"
                           "- <b>原因</b>：“file_hashes.json”文件丢失或损坏。<br>"
                           "- <b>解决方案</b>：在设置选项卡中，点击“重置文件哈希”清除去重数据，然后重新下载。应用程序将重建哈希文件以防止未来出现重复。<br><br>"
                           "<b>6.6 应用程序崩溃或冻结</b><br>"
                           "- <b>原因</b>：资源过载或程序错误。<br>"
                           "- <b>解决方案</b>：重新启动应用程序。减少“最大同时下载数”以减轻负载。检查控制台日志中的错误消息，并通过“联系与支持”部分中的 GitHub 链接报告问题。<br><br>"
                           "<b>6.7 语言未更改</b><br>"
                           "- <b>原因</b>：界面刷新问题。<br>"
                           "- <b>解决方案</b>：在设置选项卡中选择新语言后，如果更改未立即生效，请重新启动应用程序。"
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
                          "- 특히 중요하지 않은 문제에 대한 응답을 기다릴 때는 인내심을 가지세요.",
                "chinese-simplified": "如果您需要进一步的帮助或想报告错误，本节提供了获取帮助的必要信息。<br><br>"
                           "<b>7.1 GitHub 仓库</b><br>"
                           "- Kemono 下载器是一个在 GitHub 上托管的开源项目。<br>"
                           "- 访问项目页面：<a href='https://github.com/VoxDroid'>github.com/VoxDroid</a>。<br>"
                           "- 查看“Issues”选项卡，了解现有的错误报告或功能请求。如果您的问题未列出，请创建新的问题，并包含以下详细信息：<br>"
                           "  - 对问题或请求的清晰描述。<br>"
                           "  - 重现问题的步骤（如果适用）。<br>"
                           "  - 相关的控制台日志或截图。<br>"
                           "- 开发者 VoxDroid 会监控仓库，并在时间允许的情况下回应问题。<br><br>"
                           "<b>7.2 更新</b><br>"
                           "- 在 GitHub 仓库中检查最新的发布和更新。<br>"
                           "- 应用程序没有自动更新功能，因此如有需要，请从仓库手动下载最新版本。<br><br>"
                           "<b>7.3 注意事项</b><br>"
                           "- 支持由开发者和社区以志愿者形式提供。<br>"
                           "- 对于非紧急问题，等待回复时请保持耐心。"
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

