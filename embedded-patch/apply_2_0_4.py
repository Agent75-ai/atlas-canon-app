from pathlib import Path

p=Path('NarradorOffline/settings.gradle')
s=p.read_text().replace('mavenCentral()\n    }', "mavenCentral()\n        maven { url 'https://jitpack.io' }\n    }")
p.write_text(s)

p=Path('NarradorOffline/app/build.gradle')
s=p.read_text()
s=s.replace('versionCode 1', 'versionCode 6')
s=s.replace("versionName '1.0.0'", "versionName '2.0.4-neural-safe'")
s=s.replace('targetSdk 35\n', "targetSdk 35\n        ndk { abiFilters 'arm64-v8a' }\n")
s += "\n\ndependencies {\n    implementation 'com.github.k2-fsa:sherpa-onnx:v1.13.4'\n    implementation 'org.jetbrains.kotlin:kotlin-stdlib:1.7.20'\n}\n"
p.write_text(s)

p=Path('NarradorOffline/app/src/main/res/layout/activity_main.xml')
s=p.read_text()
s=s.replace('Perfil recomendado: Piper es_MX-claude-high. Voz masculina latina, calidad alta.', 'Voz integrada: Aldo · español latino es-419 · neural · offline.')
s=s.replace('android:id="@+id/btnVoxSherpa"', 'android:id="@+id/btnVoxSherpa"\n                    android:visibility="gone"')
s=s.replace('android:id="@+id/btnTtsSettings"', 'android:id="@+id/btnTtsSettings"\n                android:visibility="gone"')
p.write_text(s)

p=Path('NarradorOffline/app/src/main/java/com/gregorio/narradoroffline/NarrationService.java')
s=p.read_text()
if 'import java.io.File;' not in s:
    s=s.replace('import java.io.BufferedReader;\n', 'import java.io.BufferedReader;\nimport java.io.File;\nimport java.io.FileOutputStream;\n')

s=s.replace('        initEmbeddedTts();\n        if (!currentUri.isEmpty())', '        engineLabel = "Voz neural preparada · se inicia al reproducir";\n        if (!currentUri.isEmpty())', 1)

marker='    private volatile boolean ttsReady = false;\n'
if 'ttsInitializing' not in s:
    s=s.replace(marker, marker + '    private volatile boolean ttsInitializing = false;\n    private volatile boolean pendingTestVoice = false;\n')

s=s.replace('    private void initEmbeddedTts() {\n        engineLabel = "Cargando voz neural integrada…";\n        ttsReady = false;', '    private void initEmbeddedTts() {\n        if (ttsReady || ttsInitializing) return;\n        ttsInitializing = true;\n        engineLabel = "Preparando pronunciación española…";\n        ttsReady = false;')
s=s.replace('                OfflineTtsVitsModelConfig vits = new OfflineTtsVitsModelConfig();', '                String espeakDataDir = ensureEspeakDataDir();\n\n                OfflineTtsVitsModelConfig vits = new OfflineTtsVitsModelConfig();')
s=s.replace('                vits.setDataDir(MODEL_DIR + "/espeak-ng-data");', '                vits.setDataDir(espeakDataDir);')
s=s.replace('                tts = local;\n                ttsReady = true;', '                tts = local;\n                ttsReady = true;\n                ttsInitializing = false;')
s=s.replace('                    notifyState();\n                    if (playing) speakCurrent();', '                    notifyState();\n                    if (pendingTestVoice) { pendingTestVoice = false; testVoice(); }\n                    if (playing) speakCurrent();')
s=s.replace('            } catch (Throwable e) {\n                ttsReady = false;', '            } catch (Throwable e) {\n                ttsReady = false;\n                ttsInitializing = false;')

s=s.replace('        playing = true;\n        startForeground(NOTIFICATION_ID, buildNotification());\n        if (ttsReady) speakCurrent();\n        notifyState();', '        playing = true;\n        startForeground(NOTIFICATION_ID, buildNotification());\n        if (!ttsReady) {\n            initEmbeddedTts();\n            notifyState();\n            return;\n        }\n        speakCurrent();\n        notifyState();')

s=s.replace('    public void testVoice() {\n        if (!ttsReady) return;\n        synthesizeAndPlay(', '    public void testVoice() {\n        if (!ttsReady) {\n            pendingTestVoice = true;\n            initEmbeddedTts();\n            notifyState();\n            return;\n        }\n        pendingTestVoice = false;\n        synthesizeAndPlay(')

helper='''\n    private String ensureEspeakDataDir() throws Exception {\n        String assetRoot = MODEL_DIR + "/espeak-ng-data";\n        File target = new File(getFilesDir(), assetRoot);\n        File marker = new File(target, ".narrador-ready");\n        if (!marker.exists()) {\n            copyAssetTree(assetRoot, target);\n            if (!target.exists() && !target.mkdirs()) throw new IllegalStateException("No se pudo preparar espeak-ng-data");\n            try (FileOutputStream out = new FileOutputStream(marker)) { out.write(1); }\n        }\n        return target.getAbsolutePath();\n    }\n\n    private void copyAssetTree(String assetPath, File destination) throws Exception {\n        String[] children = getAssets().list(assetPath);\n        if (children == null) throw new IllegalStateException("No se pudo listar " + assetPath);\n        if (children.length == 0) {\n            File parent = destination.getParentFile();\n            if (parent != null && !parent.exists() && !parent.mkdirs()) throw new IllegalStateException("No se pudo crear " + parent);\n            try (InputStream in = getAssets().open(assetPath); FileOutputStream out = new FileOutputStream(destination)) {\n                byte[] buffer = new byte[16384];\n                int n;\n                while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);\n            }\n            return;\n        }\n        if (!destination.exists() && !destination.mkdirs()) throw new IllegalStateException("No se pudo crear " + destination);\n        for (String child : children) copyAssetTree(assetPath + "/" + child, new File(destination, child));\n    }\n\n'''
if 'private String ensureEspeakDataDir()' not in s:
    s=s.replace('    private String readText(Uri uri) throws Exception {', helper + '    private String readText(Uri uri) throws Exception {')

p.write_text(s)
