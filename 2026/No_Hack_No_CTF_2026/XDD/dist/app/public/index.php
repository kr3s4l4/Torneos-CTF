<?php
declare(strict_types=1);
require __DIR__ . '/../src/common.php';

page_headers();
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Folio Desk</title>
  <link rel="stylesheet" href="/assets/app.css">
</head>
<body>
  <main class="shell">
    <section class="panel">
      <h1>Folio Desk</h1>
      <form method="post" action="/draft.php">
        <label>
          Name
          <input name="name" maxlength="520" autocomplete="off" required>
        </label>
        <label>
          Memo
          <textarea name="memo" maxlength="1200" rows="9" required></textarea>
        </label>
        <label>
          Return slot
          <input name="slot" maxlength="80" autocomplete="off" required>
        </label>
        <button type="submit">Create Preview</button>
      </form>
    </section>
  </main>
</body>
</html>
