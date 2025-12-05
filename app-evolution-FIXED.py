#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKEND: ЭВОЛЮЦИЯ ОДНОГО МОНСТРА - ИСПРАВЛЕННАЯ ВЕРСИЯ
Ошибка в award_points была с полем 'stage' - исправлено!
"""

from flask import Flask, jsonify, request, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)

GAME_STATE_FILE = 'game_state.json'

# Уровни эволюции ОДНОГО монстра
EVOLUTION_STAGES = {
    1: {
        'stage': 1,
        'name': 'Морской монстр',
        'emoji': '👹',
        'max_hp': 100,
        'image': '/media/monster1.jpeg',
        'background': 'ocean_deep',
        'background_color': '#001f3f',
        'background_gradient': 'linear-gradient(135deg, #001a33 0%, #003d5c 50%, #001f3f 100%)',
        'light_intensity': 0.2,
        'water_effect': True,
        'particle_color': '#00ccff',
        'description': 'Базовая форма'
    },
    2: {
        'stage': 2,
        'name': 'Эволюция 1',
        'emoji': '🐉',
        'max_hp': 150,
        'image': '/media/monster2.jpeg',
        'background': 'ocean_mid',
        'background_color': '#004080',
        'background_gradient': 'linear-gradient(135deg, #0066cc 0%, #0099ff 50%, #004080 100%)',
        'light_intensity': 0.5,
        'water_effect': True,
        'particle_color': '#00ffff',
        'description': 'Первая эволюция'
    },
    3: {
        'stage': 3,
        'name': 'Эволюция 2',
        'emoji': '👻',
        'max_hp': 80,
        'image': '/media/monster3.jpeg',
        'background': 'ocean_shallow',
        'background_color': '#0099ff',
        'background_gradient': 'linear-gradient(135deg, #00ccff 0%, #66ffff 50%, #0099ff 100%)',
        'light_intensity': 0.8,
        'water_effect': True,
        'particle_color': '#ffffff',
        'description': 'Вторая эволюция'
    },
    4: {
        'stage': 4,
        'name': 'Финальная форма',
        'emoji': '🐲',
        'max_hp': 200,
        'image': '/media/monster4.jpeg',
        'background': 'volcano',
        'background_color': '#330000',
        'background_gradient': 'linear-gradient(135deg, #660000 0%, #ff3300 30%, #330000 100%)',
        'light_intensity': 0.6,
        'water_effect': False,
        'particle_color': '#ffaa00',
        'description': 'Финальная мега форма'
    },
}

def create_media_directory():
    """Создать директорию для медиа-файлов"""
    if not os.path.exists('media'):
        os.makedirs('media')

def load_game_state():
    """Загрузить состояние игры"""
    if os.path.exists(GAME_STATE_FILE):
        try:
            with open(GAME_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    return {
        'stage': 1,
        'current_hp': EVOLUTION_STAGES[1]['max_hp'],
        'max_hp': EVOLUTION_STAGES[1]['max_hp'],
        'last_updated': datetime.now().isoformat()
    }

def save_game_state(state):
    """Сохранить состояние игры"""
    try:
        with open(GAME_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def get_evolution_info(stage):
    """Получить информацию об эволюции по стадии"""
    stage = max(1, min(4, stage))
    return EVOLUTION_STAGES[stage]

# ==================== API ROUTES ====================

@app.route('/api/game', methods=['GET'])
def get_game_state():
    """Получить текущее состояние игры"""
    state = load_game_state()
    evolution_info = get_evolution_info(state['stage'])
    
    response_data = {
        'stage': state['stage'],
        'hp': state['current_hp'],
        'max_hp': state['max_hp'],
        'monster_name': evolution_info['name'],
        'description': evolution_info['description'],
        'emoji': evolution_info['emoji'],
        'image': evolution_info['image'],
        'background': {
            'name': evolution_info['background'],
            'color': evolution_info['background_color'],
            'gradient': evolution_info['background_gradient'],
            'light_intensity': evolution_info['light_intensity'],
            'water_effect': evolution_info['water_effect'],
            'particle_color': evolution_info['particle_color'],
        },
        'timestamp': state['last_updated']
    }
    
    print(f"📊 GET /api/game: Стадия {state['stage']}, ХП {state['current_hp']}/{state['max_hp']}")
    return jsonify(response_data)

@app.route('/api/award-points', methods=['POST'])
def award_points():
    """Учитель начисляет баллы (урон монстру)"""
    try:
        data = request.json or {}
        amount = int(data.get('amount', 0))
        
        print(f"📥 award_points: получено {amount} баллов")
        
        state = load_game_state()
        damage = max(1, amount // 10)
        
        print(f"💥 Урон: {damage}, ХП было: {state['current_hp']}")
        
        state['current_hp'] = max(0, state['current_hp'] - damage)
        state['last_updated'] = datetime.now().isoformat()
        save_game_state(state)
        
        evolution_info = get_evolution_info(state['stage'])
        
        response_data = {
            'success': True,
            'damage': damage,
            'new_hp': state['current_hp'],
            'max_hp': state['max_hp'],
            'monster_dead': state['current_hp'] <= 0,
            'stage': state['stage'],
            'monster_name': evolution_info['name']
        }
        
        print(f"✅ Новое ХП: {state['current_hp']}")
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ Ошибка award_points: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/evolve', methods=['POST'])
def evolve():
    """ЭВОЛЮЦИЯ: переход на следующую стадию"""
    try:
        state = load_game_state()
        
        old_stage = state['stage']
        
        # Максимум 4 стадии
        if old_stage >= 4:
            return jsonify({
                'success': False,
                'error': 'Монстр уже в финальной форме!'
            }), 400
        
        # Переходим на следующую стадию
        state['stage'] = old_stage + 1
        
        # Получаем информацию о новой стадии
        next_evolution = get_evolution_info(state['stage'])
        
        # Обновляем ХП
        state['current_hp'] = next_evolution['max_hp']
        state['max_hp'] = next_evolution['max_hp']
        state['last_updated'] = datetime.now().isoformat()
        
        # ВАЖНО: Сохраняем ДО отправки ответа
        save_game_state(state)
        
        response_data = {
            'success': True,
            'old_stage': old_stage,
            'new_stage': state['stage'],
            'monster_name': next_evolution['name'],
            'emoji': next_evolution['emoji'],
            'image': next_evolution['image'],
            'description': next_evolution['description'],
            'new_hp': state['current_hp'],
            'new_max_hp': state['max_hp'],
            'evolution_video': '/media/next_level.mp4',
            'background': {
                'name': next_evolution['background'],
                'color': next_evolution['background_color'],
                'gradient': next_evolution['background_gradient'],
                'light_intensity': next_evolution['light_intensity'],
                'water_effect': next_evolution['water_effect'],
                'particle_color': next_evolution['particle_color'],
            }
        }
        
        print(f"🚀 ЭВОЛЮЦИЯ: Стадия {old_stage} → {state['stage']}")
        print(f"📖 Новая форма: {next_evolution['name']}")
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ Ошибка evolve: {e}")
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
        
        print("♻️ Игра перезагружена")
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
        .header p { color: #666; font-size: 14px; }
        
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
        
        .monster-name { font-size: 28px; font-weight: bold; color: #333; margin-bottom: 5px; }
        .monster-stage { font-size: 14px; color: #999; margin-bottom: 15px; }
        .monster-description { font-size: 16px; color: #666; margin-bottom: 20px; font-style: italic; }
        
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
            <p id="stageDisplay">Стадия: <span id="stageNum">1</span>/4</p>
        </div>
        
        <div id="statusMessage" class="status"></div>
        
        <div class="monster-card">
            <img id="monsterImage" class="monster-image" src="/media/monster1.jpeg" alt="Монстр">
            <div class="monster-name" id="monsterName">Морской монстр</div>
            <div class="monster-stage" id="monsterStage">Стадия 1</div>
            <div class="monster-description" id="monsterDesc">Базовая форма</div>
            
            <div class="hp-bar-container">
                <div class="hp-bar" id="hpBar" style="width: 100%;">
                    <span id="hpText">100/100 HP</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="video-overlay" id="videoOverlay">
        <div class="video-container">
            <video id="evolutionVideo" autoplay playsinline>
                <source src="/media/next_level.mp4" type="video/mp4">
            </video>
        </div>
    </div>
    
    <script>
        let lastStage = 1;
        let lastHp = 100;
        let lastBackground = 'ocean_deep';
        let syncInProgress = false;
        
        async function syncWithServer() {
            if (syncInProgress) return;
            syncInProgress = true;
            
            try {
                const response = await fetch('/api/game');
                const data = await response.json();
                
                if (data.background && data.background.name !== lastBackground) {
                    updateBackground(data.background);
                    lastBackground = data.background.name;
                }
                
                if (data.stage > lastStage) {
                    showEvolutionAnimation(data);
                    lastStage = data.stage;
                }
                
                if (data.hp !== lastHp) {
                    animateHpChange(lastHp, data.hp, data.max_hp);
                    lastHp = data.hp;
                }
                
                document.getElementById('monsterName').textContent = data.monster_name;
                document.getElementById('stageNum').textContent = data.stage;
                document.getElementById('monsterStage').textContent = 'Стадия ' + data.stage;
                document.getElementById('monsterDesc').textContent = data.description;
                document.getElementById('monsterImage').src = data.image;
                
            } catch (error) {
                console.error('❌ Sync error:', error);
            } finally {
                syncInProgress = false;
            }
        }
        
        function updateBackground(backgroundData) {
            const body = document.body;
            body.classList.remove('bg-ocean-deep', 'bg-ocean-mid', 'bg-ocean-shallow', 'bg-volcano');
            
            const bgClassName = 'bg-' + backgroundData.name.replace(/_/g, '-');
            body.classList.add(bgClassName);
            
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
        
        async function showEvolutionAnimation(data) {
            try {
                const videoOverlay = document.getElementById('videoOverlay');
                const videoElement = document.getElementById('evolutionVideo');
                
                videoOverlay.classList.add('show');
                videoElement.src = '/media/next_level.mp4';
                
                const playPromise = videoElement.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.error('❌ Ошибка воспроизведения:', error);
                    });
                }
                
                createConfetti();
                
                videoElement.onended = () => {
                    videoOverlay.classList.remove('show');
                };
                
                setTimeout(() => {
                    videoOverlay.classList.remove('show');
                }, 8000);
                
            } catch (error) {
                console.error('❌ Ошибка видео:', error);
            }
        }
        
        function createConfetti() {
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
        
        setInterval(syncWithServer, 300);
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
        input {
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
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Назад</a>
        
        <div class="header">
            <h1>👨‍🏫 Панель учителя</h1>
            <p>Управление эволюцией монстра</p>
        </div>
        
        <div class="card">
            <h2>🎮 Атака монстра</h2>
            <div id="statusMessage" class="status"></div>
            
            <div class="form-group">
                <label>Сумма атаки:</label>
                <input type="number" id="attackInput" value="100" min="0" max="1000">
            </div>
            
            <button class="btn btn-primary" onclick="attackMonster()">⚔️ Атаковать!</button>
        </div>
        
        <div class="card">
            <h2>📊 Статус монстра</h2>
            <div id="monsterStatus" style="padding: 15px; background: #f5f5f5; border-radius: 5px; margin-bottom: 15px;">
                <p id="statusInfo">Загрузка...</p>
            </div>
            <button class="btn btn-danger" onclick="evolveMonster()">✨ ЭВОЛЮЦИЯ!</button>
        </div>
    </div>
    
    <script>
        async function updateMonsterStatus() {
            try {
                const response = await fetch('/api/game');
                const data = await response.json();
                
                const info = document.getElementById('statusInfo');
                info.innerHTML = `
                    <strong>${data.emoji} ${data.monster_name}</strong><br>
                    Стадия: ${data.stage}/4<br>
                    ХП: ${data.hp}/${data.max_hp}<br>
                    <small>${data.description}</small>
                `;
                console.log('✅ Статус обновлён:', data);
            } catch (error) {
                console.error('❌ Error updateMonsterStatus:', error);
            }
        }
        
        async function attackMonster() {
            const attackInput = document.getElementById('attackInput');
            const attack = parseInt(attackInput.value);
            
            console.log('⚔️ Отправляем атаку:', attack);
            
            if (attack <= 0) {
                showStatus('❌ Введите положительное число', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/award-points', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount: attack })
                });
                
                const data = await response.json();
                console.log('📥 Ответ от сервера:', data);
                
                if (data.success) {
                    showStatus(`⚔️ АТАКА: ${attack} баллов! Урон: ${data.damage}HP. ХП: ${data.new_hp}/${data.max_hp}`, 'success');
                    
                    if (data.monster_dead) {
                        showStatus('💀 МОНСТР ОСЛАБЛЕН! Нажмите ✨ ЭВОЛЮЦИЯ!', 'success');
                    }
                    
                    updateMonsterStatus();
                } else {
                    showStatus('❌ Ошибка: ' + data.error, 'error');
                }
            } catch (error) {
                console.error('❌ attackMonster error:', error);
                showStatus('❌ Ошибка сети: ' + error.message, 'error');
            }
        }
        
        async function evolveMonster() {
            console.log('✨ Отправляем команду эволюции');
            
            try {
                const response = await fetch('/api/evolve', { method: 'POST' });
                const data = await response.json();
                
                console.log('📥 Ответ эволюции:', data);
                
                if (data.success) {
                    showStatus(`✨ ЭВОЛЮЦИЯ! ${data.emoji} ${data.monster_name}!\\n${data.description}`, 'success');
                    updateMonsterStatus();
                } else {
                    showStatus('❌ ' + data.error, 'error');
                }
            } catch (error) {
                console.error('❌ evolveMonster error:', error);
                showStatus('❌ Ошибка: ' + error.message, 'error');
            }
        }
        
        function showStatus(message, type) {
            const elem = document.getElementById('statusMessage');
            elem.textContent = message;
            elem.className = 'status show ' + type;
            setTimeout(() => { elem.classList.remove('show'); }, 5000);
        }
        
        setInterval(updateMonsterStatus, 500);
        updateMonsterStatus();
        
        console.log('🚀 Панель учителя загружена');
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
    <title>Эволюция монстра</title>
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
        <h1>🐉 Эволюция монстра</h1>
        <div class="button-group">
            <a href="/student" class="btn btn-student">👨‍🎓 Смотреть</a>
            <a href="/teacher" class="btn btn-teacher">👨‍🏫 Управлять</a>
        </div>
    </div>
</body>
</html>
    '''

if __name__ == '__main__':
    create_media_directory()
    print("=" * 60)
    print("🚀 Запуск сервера на http://localhost:5000")
    print("🐉 ЭВОЛЮЦИЯ МОНСТРА - система активирована!")
    print("👨‍🎓 Ученик: http://localhost:5000/student")
    print("👨‍🏫 Учитель: http://localhost:5000/teacher")
    print("=" * 60)
    app.run(debug=True, port=5000, host='0.0.0.0')
