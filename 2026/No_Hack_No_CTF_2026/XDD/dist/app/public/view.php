<?php
declare(strict_types=1);
require __DIR__ . '/../src/common.php';

$id = $_GET['id'] ?? '';
if (!is_string($id) || !preg_match('/\A[a-f0-9]{32}\z/', $id)) {
    page_headers();
    http_response_code(404);
    exit('Not found');
}

$path = note_path($id);
if (!is_file($path)) {
    page_headers();
    http_response_code(404);
    exit('Not found');
}

$note = json_decode((string) file_get_contents($path), true, 8, JSON_THROW_ON_ERROR);
$name = is_string($note['name'] ?? null) ? $note['name'] : '';
$memo = is_string($note['memo'] ?? null) ? $note['memo'] : '';
$nonce = bin2hex(random_bytes(16));
$carry = $_GET['carry'] ?? '';
if (!is_string($carry)) {
    $carry = '';
}
$reserve = str_pad(substr($carry, 0, 255), 255, ' ');

$frame = folio_frame($name, $memo, $reserve);

page_headers($nonce);
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Folio Preview</title>
  <link rel="stylesheet" href="/assets/app.css">
</head>
<body>
  <main class="shell">
    <article class="document">
      <header>
        <span>Preview</span>
        <h1><?= $frame['name'] ?></h1>
      </header>
      <section class="memo"><?= $frame['memo'] ?></section>
    </article>
  </main>
</body>
</html>
