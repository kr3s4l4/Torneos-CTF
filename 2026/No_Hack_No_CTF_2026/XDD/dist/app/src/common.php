<?php
declare(strict_types=1);

const NOTE_DIR = '/tmp/folio-notes';
const DROP_DIR = '/tmp/folio-drops';

function ensure_dir(string $dir): void
{
    if (!is_dir($dir)) {
        mkdir($dir, 0700, true);
    }
}

function page_headers(?string $nonce = null): void
{
    $script = $nonce === null ? "'none'" : "'nonce-" . $nonce . "'";
    header("Content-Security-Policy: default-src 'none'; script-src {$script}; style-src 'self'; img-src 'self'; connect-src 'self' http://127.0.0.1:9100 http://localhost:9100; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'");
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: no-referrer');
    header('Cache-Control: no-store');
}

function text_field(string $key, int $limit): string
{
    $value = $_POST[$key] ?? '';
    if (!is_string($value)) {
        return '';
    }

    return substr($value, 0, $limit);
}

function html_text(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function note_path(string $id): string
{
    return NOTE_DIR . '/' . $id . '.json';
}

function drop_path(string $slot): string
{
    return DROP_DIR . '/' . hash('sha256', $slot) . '.txt';
}
