<?php
declare(strict_types=1);
require __DIR__ . '/../src/common.php';

ensure_dir(DROP_DIR);

$slot = $_GET['slot'] ?? '';
if (!is_string($slot) || $slot === '' || strlen($slot) > 120) {
    page_headers();
    http_response_code(400);
    exit('Bad slot');
}

$path = drop_path($slot);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $body = file_get_contents('php://input');
    file_put_contents($path, substr((string) $body, 0, 4096));
    header('Content-Type: text/plain; charset=utf-8');
    echo 'stored';
    exit;
}

page_headers();
$value = is_file($path) ? (string) file_get_contents($path) : '';
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Folio Return</title>
  <link rel="stylesheet" href="/assets/app.css">
</head>
<body>
  <main class="shell">
    <section class="panel">
      <h1>Returned Item</h1>
      <pre><?= html_text($value) ?></pre>
    </section>
  </main>
</body>
</html>
