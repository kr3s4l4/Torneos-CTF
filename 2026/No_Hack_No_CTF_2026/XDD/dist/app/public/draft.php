<?php
declare(strict_types=1);
require __DIR__ . '/../src/common.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /', true, 303);
    exit;
}

ensure_dir(NOTE_DIR);

$id = bin2hex(random_bytes(16));
$slot = text_field('slot', 80);
$note = [
    'name' => text_field('name', 520),
    'memo' => text_field('memo', 1200),
    'created_at' => time(),
];

file_put_contents(note_path($id), json_encode($note, JSON_THROW_ON_ERROR | JSON_INVALID_UTF8_SUBSTITUTE));

$target = '/view.php?id=' . rawurlencode($id);
if ($slot !== '') {
    $target .= '&slot=' . rawurlencode($slot);
}

header('Location: ' . $target, true, 303);
