"""Error mapping: instagrapi exceptions -> short, actionable messages for the agent."""

from instagrapi import exceptions as igx

# Specific first, generic last (isinstance walk is insertion-ordered).
_FRIENDLY: list[tuple[tuple[type[Exception], ...], str]] = [
    # Auth / session
    (
        (igx.TwoFactorRequired,),
        "2FA diperlukan. Panggil ig_login lagi dengan parameter verification_code "
        "(kode TOTP dari authenticator app user, atau 8 digit backup code).",
    ),
    (
        (igx.BadCredentials, igx.BadPassword),
        "Username atau password salah.",
    ),
    (
        (igx.LoginRequired,),
        "Session expired. Coba panggil ig_login lagi (kredensial tersimpan akan dipakai "
        "untuk relogin otomatis) atau ig_login_sessionid.",
    ),
    (
        (igx.ReloginAttemptExceeded,),
        "Gagal relogin otomatis. Minta user login manual: ig_login atau ig_login_sessionid.",
    ),
    (
        (igx.ClientNeedsUpgradeError,),
        "Instagram menolak flow login mobile dari konteks ini (error_type=needs_upgrade) - "
        "umum terjadi saat login password dari IP/perangkat baru yang belum dipercaya. "
        "Solusi paling andal: pakai ig_login_sessionid dengan cookie 'sessionid' dari browser "
        "yang sudah login ke instagram.com. Alternatif: update instagrapi ke versi terbaru, "
        "atau coba lagi nanti dari IP yang sama.",
    ),
    (
        (igx.ChallengeRequired,),
        "Instagram memicu challenge verifikasi (mis. 'was this you', selfie captcha). "
        "Selesaikan manual di aplikasi/hp user, lalu coba login lagi.",
    ),
    (
        (igx.PleaseWaitFewMinutes,),
        "Instagram minta tunggu beberapa menit (limit sementara). Tunda aksi, jangan retry sekarang.",
    ),
    (
        (igx.ClientThrottledError, igx.RateLimitError),
        "Kena rate-limit Instagram (429). Tunggu beberapa menit, kurangi frekuensi aksi.",
    ),
    # Domain not-found
    (
        (igx.UserNotFound,),
        "User tidak ditemukan (mungkin salah username/private/deactivated).",
    ),
    ((igx.MediaNotFound,), "Media tidak ditemukan."),
    ((igx.StoryNotFound,), "Story tidak ditemukan (mungkin sudah expired)."),
    ((igx.DirectThreadNotFound,), "Thread DM tidak ditemukan."),
    ((igx.HashtagNotFound,), "Hashtag tidak ditemukan."),
    ((igx.CollectionNotFound,), "Collection tidak ditemukan."),
    # Access
    (
        (igx.PrivateAccount,),
        "Akun ini private - tidak bisa diakses tanpa follow yang disetujui.",
    ),
    (
        (igx.ClientForbiddenError, igx.ClientUnauthorizedError),
        "Instagram menolak request (401/403). Bisa jadi session expired, akun dibatasi, "
        "atau konten private. Coba ig_whoami untuk cek session.",
    ),
    (
        (igx.SentryBlock,),
        "Akun diblokir sementara oleh Instagram (sentry block). Hentikan otomasi beberapa hari.",
    ),
    # Upload
    (
        (igx.PhotoNotUpload, igx.PhotoConfigureError, igx.PhotoConfigureStoryError),
        "Upload foto gagal. Cek format file (jpg/jpeg/png/webp) dan coba lagi.",
    ),
    (
        (igx.VideoNotUpload, igx.VideoConfigureError, igx.VideoConfigureStoryError),
        "Upload video gagal. Cek format (mp4) dan durasi, lalu coba lagi.",
    ),
    ((igx.ClipNotUpload,), "Upload reel gagal. Cek format (mp4) dan coba lagi."),
    ((igx.AlbumConfigureError,), "Upload album gagal."),
    # Network / HTTP
    (
        (igx.ClientNotFoundError,),
        "Endpoint/resource tidak ditemukan (404). Cek ID atau username.",
    ),
    (
        (igx.ClientConnectionError, ConnectionError),
        "Koneksi ke Instagram gagal. Cek jaringan/proxy, lalu coba lagi.",
    ),
    (
        (igx.ClientRequestTimeout,),
        "Request timeout. Coba lagi.",
    ),
]

_NOT_LOGGED_IN = (
    "Belum login. Panggil ig_login(username, password) atau ig_login_sessionid(sessionid) dulu."
)


def friendly_error(exc: Exception) -> str:
    for classes, message in _FRIENDLY:
        if isinstance(exc, classes):
            detail = str(exc).strip()
            label = type(exc).__name__
            if detail and detail not in message:
                return f"[{label}] {message} ({detail})"
            return f"[{label}] {message}"
    return f"[{type(exc).__name__}] {exc}"


def not_logged_in() -> str:
    return _NOT_LOGGED_IN
