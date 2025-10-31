<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK && isset($_POST['article_id'])) {
        $article_id = intval($_POST['article_id']);
        $file = $_FILES['image'];
        $tmp_name = $file['tmp_name'];
        $original_name = basename($file['name']);
        $file_size = $file['size'];
        $file_type = mime_content_type($tmp_name);

        // Configuration
        $allowed_types = ['image/jpeg', 'image/png', 'image/gif'];
        $max_size = 5 * 1024 * 1024; // 5MB
        $upload_dir = __DIR__ . '/uploads/';

        // Vérifier le type de fichier
        if (!in_array($file_type, $allowed_types)) {
            echo json_encode(['success' => false, 'message' => 'Type de fichier non autorisé.']);
            exit;
        }

        // Vérifier la taille du fichier
        if ($file_size > $max_size) {
            echo json_encode(['success' => false, 'message' => 'Fichier trop volumineux.']);
            exit;
        }

        // Créer le répertoire s'il n'existe pas
        if (!is_dir($upload_dir)) {
            if (!mkdir($upload_dir, 0755, true)) {
                echo json_encode(['success' => false, 'message' => 'Échec de la création du répertoire d\'uploads.']);
                exit;
            }
        }

        // Renommer le fichier pour éviter les conflits
        $ext = pathinfo($original_name, PATHINFO_EXTENSION);
        $new_name = uniqid('img_', true) . '.' . $ext;
        $upload_path = $upload_dir . $new_name;

        // Déplacer le fichier téléchargé
        if (move_uploaded_file($tmp_name, $upload_path)) {
            // Appeler le script Python
            $command = escapeshellcmd("python extract_and_update.py " . escapeshellarg($upload_path) . " " . escapeshellarg($article_id));
            $output = shell_exec($command . " 2>&1"); // Capturez également les erreurs
            file_put_contents('python_error.log', $output); // Enregistrez la sortie pour déboguer
            if (!empty($output) && floatval(trim($output)) > 0) {
                $price = floatval(trim($output));
                echo json_encode(['success' => true, 'price' => $price]);
            } else {
                file_put_contents('python_error.log', $output); // Ajout pour déboguer
                echo json_encode(['success' => false, 'message' => 'Aucun prix trouvé.']);
            }
        } else {
            error_log('move_uploaded_file a échoué pour le fichier : ' . $upload_path);
            echo json_encode(['success' => false, 'message' => 'Erreur lors du déplacement du fichier.']);
        }
    } else {
        echo json_encode(['success' => false, 'message' => 'Erreur lors du téléchargement de l\'image ou ID article manquant.']);
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Méthode de requête non autorisée.']);
}
?>