#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKEND с динамическими фонами + VIDEO анимация при уровне +1
ИСПРАВЛЕННАЯ ВЕРСИЯ - все работает правильно!
"""

from flask import Flask, jsonify, request, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)

# ==================== КОНФИГ ====================
GAME_STATE_FILE = 'game_state.json'

BOSSES = {
    1: {
        'name': 'Кракен',
        'emoji': '👹',
        'max_hp': 100,
        'image': '/media/monster1.jpeg',
        'background': 'ocean_deep',
        'background_color': '#001f3f',
        'background_gradient': 'linear-gradient(135deg, #001a33 0%, #003d5c 50%, #001f3f 100%)',
        'light_intensity': 0.2,
        'water_effect': True,
        'particle_color': '#00ccff'
    },
    2: {
        'name': 'Дракон',
        'emoji': '🐉',
        'max_hp': 150,
        'image': '/media/monster2.jpeg',
        'background': 'ocean_mid',
        'background_color': '#004080',
        'background_gradient': 'linear-gradient(135deg, #0066cc 0%, #0099ff 50%, #004080 100%)',
        'light_intensity': 0.5,
        'water_effect': True,
        'particle_color': '#00ffff'
    },
    3: {
        'name': 'Привидение',
        'emoji': '👻',
        'max_hp': 80,
        'image': '/media/monster3.jpeg',
        'background': 'ocean_shallow',
        'background_color': '#0099ff',
        'background_gradient': 'linear-gradient(135deg, #00ccff 0%, #66ffff 50%, #0099ff 100%)',
        'light_intensity': 0.8,
        'water_effect': True,
        'particle_color': '#ffffff'
    },
    4: {
        'name': 'Лавовый дракон',
        'emoji': '🐲',
        'max_hp': 200,
        'image': '/media/monster4.jpeg',
        'background': 'volcano',
        'background_color': '#330000',
        'background_gradient': 'linear-gradient(135deg, #660000 0%, #ff3300 30%, #330000 100%)',
        'light_intensity': 0.6,
        'water_effect': False,
        'particle_color': '#ffaa00'
    },
}

def create_media_directory():
    """Создать директорию для медиа-файлов если её нет"""
    if not os.path.exists('media'):
        os.makedirs('media')

def load_game_state():
    """Загрузить состояние игры из файла"""
    if os.path.exists(GAME_STATE_FILE):
        try:
            with open(GAME_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    return {
        'level': 1,
        'current_hp': BOSSES[1]['max_hp'],
        'max_hp': BOSSES[1]['max_hp'],
        'last_updated': datetime.now().isoformat()
    }

def save_game_state(state):
    """Сохранить состояние игры в файл"""
    try:
        with open(GAME_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def get_boss_info(level):
    """Получить информацию о боссе по уровню"""
    # Если уровень > 4, циклируем (5 -> 1, 6 -> 2, и т.д.)
    boss_level = ((level - 1) % len(BOSSES)) + 1
    return BOSSES[boss_level]

# ==================== API ROUTES ====================

@app.route('/api/game', methods=['GET'])
def get_game_state():
    """Получить текущее состояние игры"""
    state = load_game_state()
    boss_info = get_boss_info(state['level'])
    
    response_data = {
        'level': state['level'],
        'hp': state['current_hp'],
        'max_hp': state['max_hp'],
        'monster': boss_info['name'],
        'emoji': boss_info['emoji'],
        'image': boss_info['image'],
        'background': {
            'name': boss_info['background'],
            'color': boss_info['background_color'],
            'gradient': boss_info['background_gradient'],
            'light_intensity': boss_info['light_intensity'],
            'water_effect': boss_info['water_effect'],
            'particle_color': boss_info['particle_color'],
        },
        'timestamp': state['last_updated']
    }
    
    print(f"📊 GET /api/game: Уровень {state['level']}, ХП {state['current_hp']}/{state['max_hp']}")
    return jsonify(response_data)

@app.route('/api/award-points', methods=['POST'])
def award_points():
    """Учитель начисляет баллы (урон боссу)"""
    try:
        data = request.json or {}
        amount = int(data.get('amount', 0))
        
        state = load_game_state()
        damage = max(1, amount // 10)  # Минимум 1 урон
        
        state['current_hp'] = max(0, state['current_hp'] - damage)
        state['last_updated'] = datetime.now().isoformat()
        save_game_state(state)
        
        boss_info = get_boss_info(state['level'])
        
        response_data = {
            'success': True,
            'damage': damage,
            'new_hp': state['current_hp'],
            'max_hp': state['max_hp'],
            'boss_dead': state['current_hp'] <= 0,
            'level': state['level'],
            'monster': boss_info['name']
        }
        
        print(f"💥 award_points: Урон {damage}, осталось {state['current_hp']} ХП")
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ Ошибка award_points: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/level-up', methods=['POST'])
def level_up():
    """Переход на новый уровень"""
    try:
        state = load_game_state()
        
        # ГЛАВНОЕ: Увеличиваем уровень СНАЧАЛА
        old_level = state['level']
        state['level'] = old_level + 1
        
        # Получаем информацию о новом боссе
        next_boss = get_boss_info(state['level'])
        
        # Обновляем ХП
        state['current_hp'] = next_boss['max_hp']
        state['max_hp'] = next_boss['max_hp']
        state['last_updated'] = datetime.now().isoformat()
        
        # ВАЖНО: Сохраняем ВСЕ изменения ПЕРЕД отправкой ответа
        save_game_state(state)
        
        response_data = {
            'success': True,
            'old_level': old_level,
            'new_level': state['level'],
            'new_boss': next_boss['name'],
            'emoji': next_boss['emoji'],
            'image': next_boss['image'],
            'new_hp': state['current_hp'],
            'new_max_hp': state['max_hp'],
            'level_up_video': '/media/next_level.mp4',
            'background': {
                'name': next_boss['background'],
                'color': next_boss['background_color'],
                'gradient': next_boss['background_gradient'],
                'light_intensity': next_boss['light_intensity'],
                'water_effect': next_boss['water_effect'],
                'particle_color': next_boss['particle_color'],
            }
        }
        
        print(f"🚀 level_up: Уровень {old_level} → {state['level']}")
        print(f"📖 Новый босс: {next_boss['name']}")
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ Ошибка level_up: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Сбросить игру"""
    try:
        if os.path.exists(GAME_STATE_FILE):
            os.remove(GAME_STATE_FILE)
        
        state = load_game_state()
        save_game_state(state)
        
        print("♻️  Игра перезагружена")
        return jsonify({'success': True, 'message': 'Game reset'})
    except Exception as e:
        print(f"❌ Ошибка reset: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== МЕДИА ROUTES ====================

@app.route('/media/<filename>', methods=['GET'])
def serve_media(filename):
    """Служить медиа-файлы"""
    try:
        file_path = os.path.join('media', filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            print(f"⚠️ Файл не найден: {file_path}")
            return {'error': 'File not found'}, 404
    except Exception as e:
        print(f"❌ Ошибка serve_media: {e}")
        return {'error': str(e)}, 500

# ==================== СТРАНИЦА УЧЕНИКА ====================

@app.route('/student')
def student():
    return '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Портал ученика</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        html, body {
            font-family: 'Segoe UI', sans-serif;
            min-height: 100vh;
            padding: 20px;
            transition: background 0.8s ease-in-out;
        }
        
        /* Фоны по уровням */
        body.bg-ocean-deep {
            background: linear-gradient(135deg, #001a33 0%, #003d5c 50%, #001f3f 100%);
        }
        body.bg-ocean-mid {
            background: linear-gradient(135deg, #0066cc 0%, #0099ff 50%, #004080 100%);
        }
        body.bg-ocean-shallow {
            background: linear-gradient(135deg, #00ccff 0%, #66ffff 50%, #0099ff 100%);
        }
        body.bg-volcano {
            background: linear-gradient(135deg, #660000 0%, #ff3300 30%, #330000 100%);
        }
        
        /* По умолчанию */
        body {
            background: linear-gradient(135deg, #001a33 0%, #003d5c 50%, #001f3f 100%);
        }
        
        .container { max-width: 600px; margin: 0 auto; }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .header h1 { color: #1e5a96; margin-bottom: 10px; }
        .header p { color: #666; }
        
        .monster-card {
            background: rgba(255, 224, 178, 0.95);
            backdrop-filter: blur(10px);
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .monster-image {
            width: 200px;
            height: 200px;
            object-fit: contain;
            margin: 0 auto 15px;
            display: block;
            border-radius: 10px;
            animation: monsterAppear 0.8s ease-out;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
        }
        
        @keyframes monsterAppear {
            from { opacity: 0; transform: scale(0.5) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        
        .monster-name { font-size: 28px; font-weight: bold; color: #333; margin-bottom: 15px; }
        .monster-level { font-size: 16px; color: #666; margin-bottom: 20px; }
        
        .hp-bar-container {
            background: rgba(200, 200, 200, 0.5);
            height: 50px;
            border-radius: 25px;
            overflow: hidden;
            border: 3px solid rgba(0, 0, 0, 0.3);
        }
        .hp-bar {
            height: 100%;
            background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
            transition: width 0.6s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 16px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }
        
        .status { padding: 15px; background: rgba(255, 255, 255, 0.9); border-radius: 8px; margin-bottom: 20px; display: none; }
        .status.show { display: block; }
        
        /* ВИДЕО НА ВЕСЬ ЭКРАН */
        .video-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }
        .video-overlay.show {
            display: flex;
            animation: fadeIn 0.3s;
        }
        
        .video-container {
            width: 90%;
            max-width: 900px;
            max-height: 90vh;
        }
        
        .video-container video {
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .confetti { position: fixed; pointer-events: none; }
        .water-particle { position: fixed; pointer-events: none; opacity: 0.6; border-radius: 50%; }
        
        .back-link {
            display: inline-block;
            color: white;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Назад</a>
        
        <div class="header">
            <h1>👨‍🎓 Портал ученика</h1>
            <p id="levelDisplay">Уровень: <span id="levelNum">1</span></p>
        </div>
        
        <div id="statusMessage" class="status"></div>
        
        <div class="monster-card">
            <img id="monsterImage" class="monster-image" src="/media/monster1.jpeg" alt="Монстр">
            <div class="monster-name" id="monsterName">Кракен</div>
            <div class="monster-level">Уровень 1</div>
            
            <div class="hp-bar-container">
                <div class="hp-bar" id="hpBar" style="width: 100%;">
                    <span id="hpText">100/100 HP</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- ВИДЕО НА ВЕСЬ ЭКРАН -->
    <div class="video-overlay" id="videoOverlay">
        <div class="video-container">
            <video id="levelUpVideo" autoplay playsinline>
                <source src="/media/next_level.mp4" type="video/mp4">
                Ваш браузер не поддерживает видео
            </video>
        </div>
    </div>
    
    <script>
        let lastLevel = 1;
        let lastHp = 100;
        let lastBackground = 'ocean_deep';
        let syncInProgress = false;
        
        async function syncWithServer() {
            if (syncInProgress) return;
            syncInProgress = true;
            
            try {
                const response = await fetch('/api/game');
                const data = await response.json();
                
                console.log('📊 Sync data:', {
                    level: data.level,
                    hp: data.hp,
                    max_hp: data.max_hp,
                    bg: data.background.name
                });
                
                // Обновить фон если он изменился
                if (data.background && data.background.name !== lastBackground) {
                    console.log('🎨 Фон меняется:', lastBackground, '→', data.background.name);
                    updateBackground(data.background);
                    lastBackground = data.background.name;
                }
                
                // Проверка на новый уровень
                if (data.level > lastLevel) {
                    console.log('🚀 НОВЫЙ УРОВЕНЬ:', lastLevel, '→', data.level);
                    showLevelUpAnimation(data);
                    lastLevel = data.level;
                }
                
                // Обновить ХП если изменился
                if (data.hp !== lastHp) {
                    console.log('💚 ХП меняется:', lastHp, '→', data.hp);
                    animateHpChange(lastHp, data.hp, data.max_hp);
                    lastHp = data.hp;
                }
                
                // Обновить UI
                document.getElementById('monsterName').textContent = data.monster;
                document.getElementById('levelNum').textContent = data.level;
                document.getElementById('monsterImage').src = data.image;
                
            } catch (error) {
                console.error('❌ Sync error:', error);
            } finally {
                syncInProgress = false;
            }
        }
        
        function updateBackground(backgroundData) {
            const body = document.body;
            
            // Удалить все классы фона
            body.classList.remove('bg-ocean-deep', 'bg-ocean-mid', 'bg-ocean-shallow', 'bg-volcano');
            
            // Добавить новый класс
            const bgClassName = 'bg-' + backgroundData.name.replace(/_/g, '-');
            body.classList.add(bgClassName);
            
            console.log('✅ Фон применен:', bgClassName);
            
            if (backgroundData.water_effect) {
                createWaterParticles(backgroundData.particle_color);
            }
        }
        
        function createWaterParticles(color) {
            for (let i = 0; i < 5; i++) {
                setTimeout(() => {
                    const particle = document.createElement('div');
                    particle.className = 'water-particle';
                    particle.style.left = Math.random() * 100 + '%';
                    particle.style.top = '-20px';
                    particle.style.width = particle.style.height = Math.random() * 20 + 10 + 'px';
                    particle.style.background = color;
                    document.body.appendChild(particle);
                    
                    particle.animate([
                        { transform: 'translateY(0) translateX(0)', opacity: 0.8 },
                        { transform: `translateY(${window.innerHeight}px) translateX(${Math.random() * 100 - 50}px)`, opacity: 0 }
                    ], { duration: 3000 + Math.random() * 2000 });
                    
                    setTimeout(() => particle.remove(), 5000);
                }, i * 200);
            }
        }
        
        function animateHpChange(from, to, max) {
            const bar = document.getElementById('hpBar');
            const oldPercent = (from / max) * 100;
            const newPercent = (to / max) * 100;
            
            bar.style.width = oldPercent + '%';
            setTimeout(() => {
                bar.style.width = newPercent + '%';
                document.getElementById('hpText').textContent = to + '/' + max + ' HP';
            }, 50);
        }
        
        async function showLevelUpAnimation(data) {
            console.log('🎬 Показываем видео...');
            
            try {
                const videoOverlay = document.getElementById('videoOverlay');
                const videoElement = document.getElementById('levelUpVideo');
                
                // Показать видео
                videoOverlay.classList.add('show');
                console.log('✅ Видео-overlay показан');
                
                // Убедиться что видео есть
                const videoSrc = '/media/next_level.mp4';
                videoElement.src = videoSrc;
                
                // Попробовать воспроизвести
                const playPromise = videoElement.play();
                if (playPromise !== undefined) {
                    playPromise.then(() => {
                        console.log('✅ Видео воспроизводится');
                    }).catch(error => {
                        console.error('❌ Ошибка воспроизведения:', error);
                    });
                }
                
                // Confetti!
                createConfetti();
                
                // Закрыть после завершения видео
                videoElement.onended = () => {
                    console.log('✅ Видео закончилось');
                    videoOverlay.classList.remove('show');
                };
                
                // Или закрыть через 8 сек макс
                setTimeout(() => {
                    videoOverlay.classList.remove('show');
                    console.log('⏱️ Видео закрыто (timeout)');
                }, 8000);
                
            } catch (error) {
                console.error('❌ Ошибка видео:', error);
            }
        }
        
        function createConfetti() {
            console.log('🎉 Confetti!');
            for (let i = 0; i < 50; i++) {
                setTimeout(() => {
                    const conf = document.createElement('div');
                    conf.className = 'confetti';
                    conf.style.left = Math.random() * 100 + '%';
                    conf.style.top = '-10px';
                    conf.style.background = ['#ffeb3b', '#ff9800', '#32b8c6', '#4caf50'][Math.floor(Math.random() * 4)];
                    conf.style.width = conf.style.height = Math.random() * 10 + 5 + 'px';
                    conf.style.borderRadius = '50%';
                    document.body.appendChild(conf);
                    
                    conf.animate([
                        { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
                        { transform: `translateY(${window.innerHeight}px) rotate(${Math.random() * 360}deg)`, opacity: 0 }
                    ], { duration: 3000 });
                    
                    setTimeout(() => conf.remove(), 3000);
                }, i * 20);
            }
        }
        
        // Синхронизация каждые 300мс (быстрее!)
        setInterval(syncWithServer, 300);
        
        // Первая загрузка
        console.log('🚀 Загружаем первый раз...');
        syncWithServer();
    </script>
</body>
</html>
    '''

# ==================== СТРАНИЦА УЧИТЕЛЯ ====================

@app.route('/teacher')
def teacher():
    return '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Панель учителя</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1e5a96 0%, #32b8c6 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .header h1 { color: #1e5a96; }
        
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .card h2 { color: #1e5a96; margin-bottom: 15px; font-size: 18px; }
        .form-group { margin-bottom: 15px; }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        select, input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .btn-primary { background: #4caf50; color: white; }
        .btn-primary:hover { background: #45a049; }
        
        .btn-danger { background: #f44336; color: white; }
        .btn-danger:hover { background: #da190b; }
        
        .status {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            display: none;
        }
        .status.show { display: block; }
        .status.success { background: #c8e6c9; color: #2e7d32; }
        .status.error { background: #ffcdd2; color: #c62828; }
        
        .back-link {
            display: inline-block;
            color: white;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: bold;
        }
        
        .debug { background: #f5f5f5; padding: 10px; border-radius: 5px; font-size: 12px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Назад</a>
        
        <div class="header">
            <h1>👨‍🏫 Панель учителя</h1>
            <p>Управление игровым процессом</p>
        </div>
        
        <div class="card">
            <h2>🎮 Начислить баллы</h2>
            <div id="statusMessage" class="status"></div>
            
            <div class="form-group">
                <label>Количество баллов:</label>
                <input type="number" id="pointsInput" value="100" min="0" max="1000">
            </div>
            
            <button class="btn btn-primary" onclick="awardPoints()">✅ Начислить баллы</button>
        </div>
        
        <div class="card">
            <h2>📊 Статус</h2>
            <div id="bossStatus" style="padding: 15px; background: #f5f5f5; border-radius: 5px; margin-bottom: 15px;">
                <p id="bossInfo">Загрузка...</p>
            </div>
            <button class="btn btn-danger" onclick="levelUp()">🚀 УРОВЕНЬ +1</button>
        </div>
        
        <div class="card">
            <h2>🔧 Отладка</h2>
            <button class="btn btn-primary" onclick="resetGame()" style="background: #ff9800;">♻️ Сбросить игру</button>
            <div id="debugInfo" class="debug" style="margin-top: 10px; white-space: pre-wrap; max-height: 200px; overflow-y: auto;"></div>
        </div>
    </div>
    
    <script>
        let debugLog = [];
        
        function addDebug(msg) {
            debugLog.push('[' + new Date().toLocaleTimeString() + '] ' + msg);
            if (debugLog.length > 10) debugLog.shift();
            document.getElementById('debugInfo').textContent = debugLog.join('\\n');
        }
        
        async function updateBossStatus() {
            try {
                const response = await fetch('/api/game');
                const data = await response.json();
                
                const info = document.getElementById('bossInfo');
                info.innerHTML = `
                    <strong>${data.emoji} ${data.monster}</strong><br>
                    Уровень: ${data.level}<br>
                    ХП: ${data.hp}/${data.max_hp}
                `;
                addDebug(`Status: L${data.level} ${data.monster} ${data.hp}/${data.max_hp}HP`);
            } catch (error) {
                addDebug('❌ Status error: ' + error.message);
            }
        }
        
        async function awardPoints() {
            const points = parseInt(document.getElementById('pointsInput').value);
            
            if (points <= 0) {
                showStatus('❌ Введите положительное число', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/award-points', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount: points })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showStatus(`✅ ${points} баллов! Урон: ${data.damage}HP. Осталось: ${data.new_hp}/${data.max_hp}HP`, 'success');
                    addDebug(`Award: +${points} баллов, ${data.damage} урона`);
                    
                    if (data.boss_dead) {
                        showStatus('☠️ БОСС УБИТ! Нажмите УРОВЕНЬ +1', 'success');
                        addDebug('Boss defeated!');
                    }
                    
                    updateBossStatus();
                }
            } catch (error) {
                showStatus('❌ Ошибка: ' + error, 'error');
                addDebug('❌ Award error: ' + error);
            }
        }
        
        async function levelUp() {
            try {
                addDebug('Requesting level-up...');
                const response = await fetch('/api/level-up', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    addDebug(`✅ Level up: ${data.old_level} → ${data.new_level}`);
                    showStatus(`✅ УРОВЕНЬ ${data.new_level}!\n🎮 Новый босс: ${data.emoji} ${data.new_boss}`, 'success');
                    updateBossStatus();
                } else {
                    addDebug(`❌ Level-up failed: ${data.error}`);
                    showStatus('❌ Ошибка: ' + data.error, 'error');
                }
            } catch (error) {
                addDebug('❌ Level-up error: ' + error);
                showStatus('❌ Ошибка: ' + error, 'error');
            }
        }
        
        async function resetGame() {
            if (!confirm('Вы уверены? Это сбросит всё!')) return;
            
            try {
                const response = await fetch('/api/reset', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    showStatus('✅ Игра сброшена', 'success');
                    addDebug('Game reset');
                    updateBossStatus();
                }
            } catch (error) {
                addDebug('❌ Reset error: ' + error);
                showStatus('❌ Ошибка: ' + error, 'error');
            }
        }
        
        function showStatus(message, type) {
            const elem = document.getElementById('statusMessage');
            elem.textContent = message;
            elem.className = 'status show ' + type;
            setTimeout(() => { elem.classList.remove('show'); }, 4000);
        }
        
        setInterval(updateBossStatus, 500);
        updateBossStatus();
    </script>
</body>
</html>
    '''

# ==================== ГЛАВНАЯ ====================

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Цифровой океан знаний</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI'; background: linear-gradient(135deg, #1e5a96 0%, #32b8c6 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 40px; border-radius: 15px; text-align: center; max-width: 500px; }
        h1 { color: #1e5a96; margin-bottom: 30px; font-size: 32px; }
        .button-group { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .btn { padding: 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-decoration: none; font-size: 16px; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .btn-student { background: #4caf50; color: white; }
        .btn-teacher { background: #ff9800; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 Цифровой океан знаний</h1>
        <div class="button-group">
            <a href="/student" class="btn btn-student">👨‍🎓 Ученик</a>
            <a href="/teacher" class="btn btn-teacher">👨‍🏫 Учитель</a>
        </div>
    </div>
</body>
</html>
    '''

if __name__ == '__main__':
    create_media_directory()
    print("=" * 60)
    print("🚀 Запуск сервера на http://localhost:5000")
    print("📁 Директория 'media' создана")
    print("🎬 Видео-анимация активирована!")
    print("👨‍🎓 Ученик: http://localhost:5000/student")
    print("👨‍🏫 Учитель: http://localhost:5000/teacher")
    print("=" * 60)
    app.run(debug=True, port=5000, host='0.0.0.0')
