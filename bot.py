import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta
import json

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Dicionário para armazenar as configurações dos canais de housing
housing_channels = {}

# Dicionário para armazenar as notificações dos usuários
user_notifications = {}

# Dicionário para armazenar o último status conhecido de cada casa
last_known_status = {}

# Função para salvar as configurações dos canais
def save_housing_channels():
    with open('housing_channels.json', 'w') as f:
        json.dump(housing_channels, f, indent=4)

# Função para carregar as configurações dos canais
def load_housing_channels():
    try:
        with open('housing_channels.json', 'r') as f:
            content = f.read()
            if not content:  # Se o arquivo estiver vazio
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver mal formatado, cria um novo
        with open('housing_channels.json', 'w') as f:
            json.dump({}, f, indent=4)
        return {}

# Função para salvar as notificações dos usuários
def save_user_notifications():
    with open('user_notifications.json', 'w') as f:
        json.dump(user_notifications, f, indent=4)

# Função para salvar o último status conhecido
def save_last_known_status():
    with open('last_known_status.json', 'w') as f:
        json.dump(last_known_status, f, indent=4)

# Função para carregar as notificações dos usuários
def load_user_notifications():
    try:
        with open('user_notifications.json', 'r') as f:
            content = f.read()
            if not content:  # Se o arquivo estiver vazio
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver mal formatado, cria um novo
        with open('user_notifications.json', 'w') as f:
            json.dump({}, f, indent=4)
        return {}

# Função para carregar o último status conhecido
def load_last_known_status():
    try:
        with open('last_known_status.json', 'r') as f:
            content = f.read()
            if not content:  # Se o arquivo estiver vazio
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver mal formatado, cria um novo
        with open('last_known_status.json', 'w') as f:
            json.dump({}, f, indent=4)
        return {}

# Carrega as configurações salvas
housing_channels = load_housing_channels()

# Carrega as notificações salvas
user_notifications = load_user_notifications()

# Carrega o último status conhecido
last_known_status = load_last_known_status()

# Dicionário de data centers e mundos
DATA_CENTERS = {
    'primal': ['behemoth', 'excalibur', 'lamia', 'leviathan', 'ultros'],
    'aether': ['adamantoise', 'cactuar', 'faerie', 'gilgamesh', 'jenova', 'midgardsormr', 'sargatanas', 'siren'],
    'crystal': ['balmung', 'brynhildr', 'coeurl', 'diabolos', 'goblin', 'malboro', 'mateus', 'zalera'],
    'dynamis': ['halicarnassus', 'maduin', 'marilith', 'seraph'],
    'light': ['alpha', 'lich', 'odin', 'phoenix', 'raiden', 'shiva', 'twintania', 'zodiark'],
    'chaos': ['cerberus', 'louisoix', 'moogle', 'omega', 'ragnarok', 'spriggan'],
    'elemental': ['aegis', 'atomos', 'carbuncle', 'garuda', 'gungnir', 'kujata', 'ramuh', 'tonberry', 'typhon', 'unicorn'],
    'gaia': ['alexander', 'bahamut', 'durandal', 'fenrir', 'ifrit', 'ridill', 'tiamat', 'ultima', 'valefor', 'yojimbo', 'zeromus'],
    'mana': ['anima', 'asura', 'belias', 'chocobo', 'hades', 'ixion', 'mandragora', 'masamune', 'pandaemonium', 'shinryu', 'titan'],
    'meteor': ['bismarck', 'ravana', 'sephirot', 'sophia', 'susano', 'zurvan']
}

# IDs dos mundos
WORLD_IDS = {
    # Primal
    'behemoth': 78,
    'excalibur': 93,
    'lamia': 55,
    'leviathan': 64,
    'ultros': 77,
    'exodus': 53,
    'famfrit': 35,
    'hyperion': 95,
    
    # Aether
    'adamantoise': 73,
    'cactuar': 79,
    'faerie': 54,
    'gilgamesh': 63,
    'jenova': 40,
    'midgardsormr': 65,
    'sargatanas': 99,
    'siren': 57,
    
    # Crystal
    'balmung': 91,
    'brynhildr': 34,
    'coeurl': 74,
    'diabolos': 62,
    'goblin': 81,
    'malboro': 75,
    'mateus': 37,
    'zalera': 41,
    
    # Dynamis
    'halicarnassus': 406,
    'maduin': 407,
    'marilith': 404,
    'seraph': 405,
    'cuchulainn': 408,
    'kraken': 409,
    'rafflesia': 410,
    'golem': 411,
    
    # Light
    'alpha': 402,
    'lich': 36,
    'odin': 66,
    'phoenix': 56,
    'raiden': 403,
    'shiva': 67,
    'twintania': 33,
    'zodiark': 42,
    
    # Chaos
    'cerberus': 80,
    'louisoix': 83,
    'moogle': 71,
    'omega': 39,
    'ragnarok': 97,
    'spriggan': 85,
    'sagittarius': 400,
    'phantom': 401,
    
    # Elemental
    'aegis': 90,
    'atomos': 68,
    'carbuncle': 45,
    'garuda': 58,
    'gungnir': 94,
    'kujata': 49,
    'ramuh': 60,
    'tonberry': 72,
    'typhon': 50,
    'unicorn': 30,
    
    # Gaia
    'alexander': 43,
    'bahamut': 69,
    'durandal': 92,
    'fenrir': 46,
    'ifrit': 59,
    'ridill': 98,
    'tiamat': 76,
    'ultima': 51,
    'valefor': 52,
    'yojimbo': 31,
    'zeromus': 32,
    
    # Mana
    'anima': 44,
    'asura': 23,
    'belias': 24,
    'chocobo': 70,
    'hades': 47,
    'ixion': 48,
    'mandragora': 82,
    'masamune': 96,
    'pandaemonium': 28,
    'shinryu': 29,
    'titan': 61,
    
    # Meteor
    'bismarck': 22,
    'ravana': 21,
    'sephirot': 86,
    'sophia': 87,
    'susano': 89,
    'zurvan': 88
}

# Tamanhos de casa disponíveis
HOUSE_SIZES = ['small', 'medium', 'large']

# Distritos disponíveis
DISTRICTS = ['shirogane', 'lavender beds', 'mist', 'goblet', 'empyreum']

# Mapeamento de IDs dos distritos para nomes
DISTRICT_IDS = {
    339: "Mist",
    340: "The Lavender Beds",
    341: "The Goblet",
    641: "Shirogane",
    979: "Empyreum"
}

# Mapeamento de tamanhos
SIZE_NAMES = {
    0: "Small",
    1: "Medium",
    2: "Large"
}

# Mapeamento de fases da loteria
LOTTO_PHASES = {
    3: "❌ Indisponível",
    2: "📊 Resultados",
    1: "✅ Disponível"
}

# Adiciona as cores e emojis para cada distrito
DISTRICT_COLORS = {
    "Mist": discord.Color.blue(),  # Azul para Mist (praia)
    "The Lavender Beds": discord.Color.purple(),  # Roxo para Lavender Beds
    "The Goblet": discord.Color.orange(),  # Laranja para Goblet (deserto)
    "Shirogane": discord.Color.from_rgb(255, 182, 193),  # Rosa claro para Shirogane (cerejeiras)
    "Empyreum": discord.Color.from_rgb(135, 206, 235)  # Azul céu para Empyreum
}

DISTRICT_EMOJIS = {
    "Mist": "🌊",  # Praia
    "The Lavender Beds": "🌸",  # Flores
    "The Goblet": "🏺",  # Vaso/Ânfora
    "Shirogane": "🎋",  # Bambu
    "Empyreum": "❄️"  # Neve
}

# Emojis para tamanhos
SIZE_EMOJIS = {
    "Small": "🏠",
    "Medium": "🏡",
    "Large": "🏰"
}

@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Sincronizado {len(synced)} comando(s)')
        
        # Inicia a task de atualização se não estiver rodando
        if not update_housing_channels.is_running():
            update_housing_channels.start()
            print("Task de atualização de canais iniciada!")
        
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

def get_house_data(data_center, world, size=None, district=None):
    base_url = "https://paissadb.zhu.codes"
    world_id = WORLD_IDS.get(world.lower())
    if not world_id:
        raise ValueError(f"ID do mundo {world} não encontrado")
    
    url = f"{base_url}/worlds/{world_id}"
    print(f"Buscando URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        
        # Processa os dados da API
        houses = []
        
        # Itera sobre os distritos
        for district_data in data.get('districts', []):
            district_name = DISTRICT_IDS.get(district_data.get('id'), "Unknown")
            
            # Itera sobre os plots abertos no distrito
            for plot in district_data.get('open_plots', []):
                house_data = {
                    'district': district_name,
                    'ward': plot.get('ward_number', 0) + 1,  # Adiciona 1 ao ward
                    'plot': plot.get('plot_number', 0) + 1,  # Adiciona 1 ao plot
                    'size': SIZE_NAMES.get(plot.get('size', 0), 'Unknown'),
                    'price': plot.get('price', 0),
                    'lotto_entries': plot.get('lotto_entries', None),
                    'purchase_system': plot.get('purchase_system', 0),
                    'lotto_phase': plot.get('lotto_phase', None),
                    'lotto_phase_until': plot.get('lotto_phase_until', None),
                }
                
                # Aplica os filtros opcionais
                if size:
                    size_map = {"small": "Small", "medium": "Medium", "large": "Large"}
                    if house_data['size'] != size_map.get(size.lower()):
                        continue
                
                if district and district.lower() not in district_name.lower():
                    continue
                
                houses.append(house_data)
        
        return houses
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return []
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        import traceback
        print(traceback.format_exc())
        return []

@bot.tree.command(name="housing_check", description="Busca casas disponíveis com filtros específicos")
async def casas_para_comprar(
    interaction: discord.Interaction,
    data_center: str,
    world: str,
    tamanho: str = None,
    distrito: str = None
):
    await interaction.response.defer()
    
    # Validação dos parâmetros
    data_center = data_center.lower()
    world = world.lower()
    
    if data_center not in DATA_CENTERS:
        await interaction.followup.send(f"Data center inválido. Data centers disponíveis: {', '.join(DATA_CENTERS.keys())}")
        asyncio.sleep(15)
        await interaction.delete_original_response()
        return
    
    if world not in DATA_CENTERS[data_center]:
        await interaction.followup.send(f"Mundo inválido para o data center {data_center}. Mundos disponíveis: {', '.join(DATA_CENTERS[data_center])}")
        asyncio.sleep(15)
        await interaction.delete_original_response()    
        return
    
    if tamanho and tamanho.lower() not in HOUSE_SIZES:
        await interaction.followup.send(f"Tamanho inválido. Tamanhos disponíveis: {', '.join(HOUSE_SIZES)}")
        asyncio.sleep(15)  # Espera 5 segundos antes de apagar a mensagem
        await interaction.delete_original_response()
        return
    
    if distrito and distrito.lower() not in DISTRICTS:
        await interaction.followup.send(f"Distrito inválido. Distritos disponíveis: {', '.join(DISTRICTS)}")
        asyncio.sleep(15)
        await interaction.delete_original_response()
        return
    
    # Busca os dados das casas
    houses = get_house_data(data_center, world, tamanho, distrito)
    
    if not houses:
        await interaction.followup.send("Nenhuma casa encontrada com os filtros especificados.")
        return
    
    # Organiza as casas por distrito
    houses_by_district = {}
    for house in houses:
        # Mostra apenas casas em loteria (purchase_system = 7)
        if house['purchase_system'] != 7:
            continue
            
        district = house['district']
        if district not in houses_by_district:
            houses_by_district[district] = []
        houses_by_district[district].append(house)

    # Cria embeds por distrito
    embeds = []
    for district, district_houses in houses_by_district.items():
        embed = discord.Embed(
            title=f"{DISTRICT_EMOJIS.get(district, '🏘️')} {district}",
            description=f"Mundo: **{world.capitalize()}** ({data_center.capitalize()})",
            color=DISTRICT_COLORS.get(district, discord.Color.blue()),
            timestamp=discord.utils.utcnow()
        )
        
        # Ordena as casas por tamanho e depois por preço
        district_houses.sort(key=lambda x: (["Small", "Medium", "Large"].index(x['size']), x['price']))
        
        for house in district_houses:
            # Formata o sistema de compra (sempre será loteria)
            entries = house['lotto_entries'] if house['lotto_entries'] is not None else "?"
            purchase_info = f"🎫 Loteria (Inscrições: {entries})"
            
            # Adiciona a fase da loteria
            lotto_phase = LOTTO_PHASES.get(house['lotto_phase'], "❓ Unknown")
            purchase_info = f"🎫 Loteria (Inscrições: {entries})\n📌 Status: {lotto_phase}"
            
            # Adiciona até quando vai a fase da loteria, se disponível
            if house.get('lotto_phase_until'):
                try:
                    from datetime import timezone, timedelta
                    until_dt = datetime.utcfromtimestamp(house['lotto_phase_until']) - timedelta(hours=3)
                    until_str = until_dt.strftime('%d/%m/%Y %H:%M')
                    purchase_info += f"\n⏰ Até: {until_str} (Brasília)"
                except Exception:
                    pass
            
            # Formata o preço em milhões se for maior que 1M
            price = house['price']
            if price >= 1000000:
                price_text = f"{price/1000000:.1f}M gil"
            else:
                price_text = f"{price:,} gil"
            
            size_emoji = SIZE_EMOJIS.get(house['size'], "🏠")
            
            value_text = (
                f"{size_emoji} **{house['size']}**\n"
                f"💰 {price_text}\n"
                f"📍 {purchase_info}"
            )
            
            embed.add_field(
                name=f"Ward {house['ward']} • Plot {house['plot']}",
                value=value_text,
                inline=False
            )
        
        total_houses = len(district_houses)
        embed.set_footer(text=f"Total de casas disponíveis: {total_houses}")
        
        if total_houses > 0:
            # Adiciona um campo com estatísticas
            stats = {
                "Small": len([h for h in district_houses if h['size'] == "Small"]),
                "Medium": len([h for h in district_houses if h['size'] == "Medium"]),
                "Large": len([h for h in district_houses if h['size'] == "Large"])
            }
            
            stats_text = " • ".join([
                f"{SIZE_EMOJIS[size]} {count}" for size, count in stats.items() if count > 0
            ])
            
            embed.add_field(
                name="📊 Distribuição",
                value=stats_text,
                inline=False
            )
        
        # Adiciona campo para o contador
        embed.add_field(
            name="⏳ Tempo Até Apagar a Mensagem",
            value="5:00",
            inline=False
        )
        
        embeds.append(embed)
    
    # Envia as embeds e inicia o contador
    sent_messages = []
    for embed in embeds:
        message = await interaction.followup.send(embed=embed)
        sent_messages.append(message)
    
    # Função para atualizar o contador
    end_time = datetime.utcnow() + timedelta(minutes=1)
    
    while datetime.utcnow() < end_time:
        time_left = end_time - datetime.utcnow()
        minutes = int(time_left.total_seconds() // 60)
        seconds = int(time_left.total_seconds() % 60)
        
        for message, embed in zip(sent_messages, embeds):
            # Atualiza o campo do contador em cada embed
            embed.set_field_at(
                -1,  # Último campo (contador)
                name="⏳ Tempo Restante",
                value=f"{minutes:02d}:{seconds:02d}",
                inline=False
            )
            try:
                await message.edit(embed=embed)
            except discord.NotFound:
                continue  # Ignora se a mensagem já foi deletada
        
        await asyncio.sleep(10)  # Atualiza a cada 10 segundos
    
    # Remove as mensagens após o tempo
    for message in sent_messages:
        try:
            await message.delete()
        except discord.NotFound:
            continue  # Ignora se a mensagem já foi deletada

@bot.tree.command(name="set_housing_channel", description="Configura um canal para monitorar casas disponíveis")
async def set_housing_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    world: str,
    district: str = None
):
    # Verifica se o usuário tem permissão para gerenciar canais
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Você precisa ter permissão para gerenciar canais para usar este comando.", ephemeral=True)
        return

    # Validação do mundo
    world = world.lower()
    world_found = False
    for dc in DATA_CENTERS.values():
        if world in dc:
            world_found = True
            break
    
    if not world_found:
        await interaction.response.send_message(f"Mundo inválido. Por favor, escolha um mundo válido.", ephemeral=True)
        return

    # Validação do distrito (se fornecido)
    if district and district.lower() not in DISTRICTS:
        await interaction.response.send_message(f"Distrito inválido. Distritos disponíveis: {', '.join(DISTRICTS)}", ephemeral=True)
        return

    # Salva a configuração
    guild_id = str(interaction.guild_id)
    channel_id = str(channel.id)
    
    # Inicializa a estrutura do servidor se não existir
    if guild_id not in housing_channels:
        housing_channels[guild_id] = {
            "guild_name": interaction.guild.name,
            "channels": {}
        }
    
    # Adiciona ou atualiza a configuração do canal
    housing_channels[guild_id]["channels"][channel_id] = {
        "channel_name": channel.name,
        "world": world,
        "district": district.lower() if district else None,
        "messages": []
    }
    save_housing_channels()

    await interaction.response.send_message(f"Canal {channel.mention} configurado para monitorar casas em {world.capitalize()}" + 
                                          (f" no distrito {district.capitalize()}" if district else ""), ephemeral=True)

class NotificationButton(discord.ui.View):
    def __init__(self, house_data, world, timeout=1800):  # 30 minutos de timeout
        super().__init__(timeout=timeout)
        self.house_data = house_data
        self.world = world

    @discord.ui.button(label="🔔 Ativar Notificações", style=discord.ButtonStyle.primary)
    async def notify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        # Cria uma chave única para a casa
        house_key = f"{self.world}_{self.house_data['district']}_{self.house_data['ward']}_{self.house_data['plot']}"
        
        # Inicializa o dicionário do usuário se não existir
        if user_id not in user_notifications:
            user_notifications[user_id] = {
                "notifications": [],
                "username": str(interaction.user)
            }
        
        # Verifica se o usuário já está notificando esta casa
        if house_key in user_notifications[user_id]["notifications"]:
            try:
                embed = discord.Embed(
                    title="⚠️ Notificação Já Ativa",
                    description="Você já está recebendo notificações para esta casa!",
                    color=discord.Color.yellow()
                )
                await interaction.user.send(embed=embed)
            except discord.Forbidden:
                await interaction.response.send_message("Não foi possível enviar a mensagem de confirmação. Verifique se você tem DMs abertas!", ephemeral=True)
            return
        
        # Adiciona a notificação
        user_notifications[user_id]["notifications"].append(house_key)
        save_user_notifications()
        
        # Salva o status atual como último status conhecido
        last_known_status[house_key] = {
            "lotto_phase": self.house_data['lotto_phase'],
            "lotto_entries": self.house_data['lotto_entries'],
            "lotto_phase_until": self.house_data.get('lotto_phase_until')
        }
        save_last_known_status()
        
        # Envia confirmação via DM
        try:
            embed = discord.Embed(
                title="🔔 Notificação Ativada",
                description="Você receberá notificações sobre mudanças no status desta casa.",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            # Adiciona informações da casa
            embed.add_field(
                name="🏰 Localização",
                value=f"{self.house_data['district']} - Ward {self.house_data['ward']} Plot {self.house_data['plot']}",
                inline=False
            )
            
            embed.add_field(
                name="🌍 Mundo",
                value=self.world.capitalize(),
                inline=False
            )
            
            # Adiciona informações do status atual
            lotto_phase = LOTTO_PHASES.get(self.house_data['lotto_phase'], "❓ Unknown")
            entries = self.house_data['lotto_entries'] if self.house_data['lotto_entries'] is not None else "?"
            
            embed.add_field(
                name="📊 Status Atual",
                value=f"Status: {lotto_phase}\nInscrições: {entries}",
                inline=False
            )
            
            # Adiciona dica sobre gerenciamento
            embed.add_field(
                name="💡 Dica",
                value="Use o comando `/my_notifications` para gerenciar suas notificações.",
                inline=False
            )
            
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("✅ Notificação ativada! Verifique suas mensagens diretas.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Não foi possível enviar a mensagem de confirmação. Verifique se você tem DMs abertas!", ephemeral=True)

# Modifique a função que cria os embeds para incluir os botões
def create_house_embed(house, world):
    embed = discord.Embed(
        title=f"{DISTRICT_EMOJIS.get(house['district'], '🏘️')} {house['district']}",
        description=f"Mundo: **{world.capitalize()}**",
        color=DISTRICT_COLORS.get(house['district'], discord.Color.blue()),
        timestamp=discord.utils.utcnow()
    )

    # Formata o sistema de compra (sempre será loteria)
    entries = house['lotto_entries'] if house['lotto_entries'] is not None else "?"
    purchase_info = f"🎫 Loteria (Inscrições: {entries})"
    
    # Adiciona a fase da loteria
    lotto_phase = LOTTO_PHASES.get(house['lotto_phase'], "❓ Unknown")
    purchase_info = f"🎫 Loteria (Inscrições: {entries})\n📌 Status: {lotto_phase}"

    # Adiciona até quando vai a fase da loteria, se disponível
    if house.get('lotto_phase_until'):
        try:
            from datetime import timezone, timedelta
            until_dt = datetime.utcfromtimestamp(house['lotto_phase_until']) - timedelta(hours=3)
            until_str = until_dt.strftime('%d/%m/%Y %H:%M')
            purchase_info += f"\n⏰ Até: {until_str} (Brasília)"
        except Exception:
            pass

    # Formata o preço em milhões se for maior que 1M
    price = house['price']
    if price >= 1000000:
        price_text = f"{price/1000000:.1f}M gil"
    else:
        price_text = f"{price:,} gil"

    size_emoji = SIZE_EMOJIS.get(house['size'], "🏠")

    value_text = (
        f"{size_emoji} **{house['size']}**\n"
        f"💰 {price_text}\n"
        f"📍 {purchase_info}"
    )

    embed.add_field(
        name=f"Ward {house['ward']} • Plot {house['plot']}",
        value=value_text,
        inline=False
    )

    return embed

# Modifique a função update_housing_channels para usar o novo sistema de embeds e botões
@tasks.loop(minutes=30)
async def update_housing_channels():
    # Proteção para evitar execução duplicada
    if getattr(update_housing_channels, '_running', False):
        print('Task já está rodando, abortando execução duplicada.')
        return
    update_housing_channels._running = True
    try:
        # Cria uma cópia do dicionário para iteração segura
        guilds_data = dict(housing_channels)
        
        for guild_id, guild_data in guilds_data.items():
            # Cria uma cópia do dicionário de canais para iteração segura
            channels_data = dict(guild_data["channels"])
            
            for channel_id, channel_config in channels_data.items():
                try:
                    guild = bot.get_guild(int(guild_id))
                    if not guild:
                        continue

                    channel = guild.get_channel(int(channel_id))
                    if not channel:
                        continue

                    # Busca as casas disponíveis
                    houses = get_house_data(None, channel_config['world'], None, channel_config['district'])
                    
                    if not houses:
                        continue

                    # Deleta as mensagens antigas
                    for message_id in channel_config['messages']:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.delete()
                        except:
                            pass

                    # Limpa a lista de mensagens
                    channel_config['messages'] = []

                    # Cria e envia o embed do cabeçalho
                    header_embed = discord.Embed(
                        title=f"🏰 {channel_config['world'].capitalize()}",
                        description=f"Casas disponíveis no {channel_config['world'].capitalize()}:",
                        color=discord.Color.gold(),
                        timestamp=discord.utils.utcnow()
                    )
                    header_message = await channel.send(embed=header_embed)
                    channel_config['messages'].append(header_message.id)

                    # Organiza as casas por distrito
                    houses_by_district = {}
                    for house in houses:
                        # Mostra apenas casas em loteria (purchase_system = 7)
                        if house['purchase_system'] != 7:
                            continue
                            
                        district = house['district']
                        if district not in houses_by_district:
                            houses_by_district[district] = []
                        houses_by_district[district].append(house)

                    # Cria embeds por distrito
                    for district, district_houses in houses_by_district.items():
                        # Ordena as casas por tamanho e depois por preço
                        district_houses.sort(key=lambda x: (["Small", "Medium", "Large"].index(x['size']), x['price']))
                        
                        # Cria o embed do distrito
                        district_embed = discord.Embed(
                            title=f"{DISTRICT_EMOJIS.get(district, '🏘️')} {district}",
                            description=f"Mundo: **{channel_config['world'].capitalize()}**",
                            color=DISTRICT_COLORS.get(district, discord.Color.blue()),
                            timestamp=discord.utils.utcnow()
                        )
                        
                        # Adiciona estatísticas do distrito
                        stats = {
                            "Small": len([h for h in district_houses if h['size'] == "Small"]),
                            "Medium": len([h for h in district_houses if h['size'] == "Medium"]),
                            "Large": len([h for h in district_houses if h['size'] == "Large"])
                        }
                        
                        stats_text = " • ".join([
                            f"{SIZE_EMOJIS[size]} {count}" for size, count in stats.items() if count > 0
                        ])
                        
                        district_embed.add_field(
                            name="📊 Distribuição",
                            value=stats_text,
                            inline=False
                        )
                        
                        # Envia o embed do distrito
                        district_message = await channel.send(embed=district_embed)
                        channel_config['messages'].append(district_message.id)
                        
                        # Cria um embed para cada casa no distrito
                        for house in district_houses:
                            embed = create_house_embed(house, channel_config['world'])
                            view = NotificationButton(house, channel_config['world'])
                            message = await channel.send(embed=embed, view=view)
                            channel_config['messages'].append(message.id)
                            
                            # Verifica se há usuários para notificar sobre mudanças
                            for user_id, user_data in user_notifications.items():
                                house_key = f"{channel_config['world']}_{district}_{house['ward']}_{house['plot']}"
                                if house_key in user_data["notifications"]:
                                    # Verifica se houve mudança no status
                                    current_status = {
                                        "lotto_phase": house['lotto_phase'],
                                        "lotto_entries": house['lotto_entries'],
                                        "lotto_phase_until": house.get('lotto_phase_until')
                                    }
                                    
                                    last_status = last_known_status.get(house_key, {})
                                    
                                    # Só envia notificação se houver mudança real
                                    if (current_status["lotto_phase"] != last_status.get("lotto_phase") or
                                        current_status["lotto_entries"] != last_status.get("lotto_entries") or
                                        current_status["lotto_phase_until"] != last_status.get("lotto_phase_until")):
                                        
                                        # Atualiza o último status conhecido
                                        last_known_status[house_key] = current_status
                                        save_last_known_status()
                                        
                                        user = await bot.fetch_user(int(user_id))
                                        if user:
                                            try:
                                                embed = discord.Embed(
                                                    title="🔔 Atualização de Status",
                                                    description="O status de uma casa que você está monitorando mudou!",
                                                    color=discord.Color.blue(),
                                                    timestamp=discord.utils.utcnow()
                                                )
                                                
                                                # Adiciona informações da casa
                                                embed.add_field(
                                                    name="🏰 Localização",
                                                    value=f"{district} - Ward {house['ward']} Plot {house['plot']}",
                                                    inline=False
                                                )
                                                
                                                embed.add_field(
                                                    name="🌍 Mundo",
                                                    value=channel_config['world'].capitalize(),
                                                    inline=False
                                                )
                                                
                                                # Adiciona informações do novo status
                                                lotto_phase = LOTTO_PHASES.get(house['lotto_phase'], "❓ Unknown")
                                                entries = house['lotto_entries'] if house['lotto_entries'] is not None else "?"
                                                
                                                embed.add_field(
                                                    name="📊 Novo Status",
                                                    value=f"Status: {lotto_phase}\nInscrições: {entries}",
                                                    inline=False
                                                )
                                                
                                                # Adiciona até quando vai a fase da loteria, se disponível
                                                if house.get('lotto_phase_until'):
                                                    try:
                                                        from datetime import timezone, timedelta
                                                        until_dt = datetime.utcfromtimestamp(house['lotto_phase_until']) - timedelta(hours=3)
                                                        until_str = until_dt.strftime('%d/%m/%Y %H:%M')
                                                        embed.add_field(
                                                            name="⏰ Próxima Mudança",
                                                            value=f"{until_str} (Brasília)",
                                                            inline=False
                                                        )
                                                    except Exception:
                                                        pass
                                                
                                                await user.send(embed=embed)
                                            except Exception as e:
                                                print(f"Erro ao enviar notificação para {user_id}: {e}")

                    # Atualiza o dicionário original com as novas mensagens
                    housing_channels[guild_id]["channels"][channel_id] = channel_config
                    save_housing_channels()

                except Exception as e:
                    print(f"Erro ao atualizar canal {channel_id} no servidor {guild_id}: {e}")
                
                # Adiciona um delay de 30 segundos entre cada canal
                await asyncio.sleep(30)
    finally:
        update_housing_channels._running = False

@update_housing_channels.before_loop
async def before_update_housing_channels():
    await bot.wait_until_ready()

@bot.tree.command(name="housing_help", description="Explica como usar o comando de verificação de casas")
async def housing_help(interaction: discord.Interaction):
    # Verifica se o usuário tem permissão de administrador
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Você precisa ter permissão de administrador para usar este comando.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🏰 Guia do Comando Housing Check",
        description="Explicação detalhada do comando `/housing_check`",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📝 Como Usar",
        value="Use o comando `/housing_check` seguido dos parâmetros necessários:",
        inline=False
    )

    embed.add_field(
        name="🔍 Parâmetros Obrigatórios",
        value=(
            "• `data_center`: O data center do mundo (ex: primal, aether, crystal)\n"
            "• `world`: O mundo específico (ex: behemoth, excalibur, lamia)"
        ),
        inline=False
    )

    embed.add_field(
        name="🔧 Parâmetros Opcionais",
        value=(
            "• `tamanho`: Filtra por tamanho da casa (small, medium, large)\n"
            "• `distrito`: Filtra por distrito específico (shirogane, lavender beds, mist, goblet, empyreum)"
        ),
        inline=False
    )

    embed.add_field(
        name="📊 Informações Exibidas",
        value=(
            "Para cada casa disponível, você verá:\n"
            "• 🏠 Tamanho da casa\n"
            "• 💰 Preço em gil\n"
            "• 🎫 Número de inscrições na loteria\n"
            "• 📌 Status da loteria:\n"
            "  - ✅ Disponível: Casa está disponível para inscrição\n"
            "  - 📊 Resultados: Período de resultados da loteria\n"
            "  - ❌ Indisponível: Casa não está disponível"
        ),
        inline=False
    )

    embed.add_field(
        name="⏱️ Duração",
        value="As mensagens são exibidas por 1 minuto e depois são automaticamente removidas.",
        inline=False
    )

    embed.add_field(
        name="📝 Exemplo",
        value="`/housing_check data_center:primal world:behemoth tamanho:small distrito:shirogane`",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="housing_status", description="Verifica o status da atualização de canais de housing")
async def housing_status(interaction: discord.Interaction):
    # Verifica se o usuário tem permissão de administrador ou gerenciar canais
    if not (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_channels):
        await interaction.response.send_message("Você precisa ter permissão de administrador ou gerenciar canais para usar este comando.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🏰 Status da Atualização de Canais",
        color=discord.Color.blue()
    )

    # Verifica se a task está rodando
    is_running = update_housing_channels.is_running()
    status_text = "✅ Rodando" if is_running else "❌ Parada"
    embed.add_field(name="Status da Task", value=status_text, inline=False)

    # Conta quantos canais estão configurados
    total_channels = sum(len(guild_data["channels"]) for guild_data in housing_channels.values())
    embed.add_field(name="Canais Configurados", value=str(total_channels), inline=False)

    # Adiciona botão para forçar atualização
    if not is_running:
        embed.add_field(
            name="⚠️ Aviso",
            value="A task de atualização está parada. Use o botão abaixo para reiniciar.",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

    # Se a task não estiver rodando, oferece botão para reiniciar
    if not is_running:
        class RestartButton(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)  # 5 minutos de timeout

            @discord.ui.button(label="Reiniciar Atualização", style=discord.ButtonStyle.green)
            async def restart_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if not update_housing_channels.is_running():
                    update_housing_channels.start()
                    await interaction.response.send_message("✅ Task de atualização reiniciada!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ A task já está rodando!", ephemeral=True)

        await interaction.followup.send("Clique no botão abaixo para reiniciar a atualização:", view=RestartButton())

@bot.tree.command(name="clear_houses", description="Limpa todas as mensagens de um canal (admin)")
@app_commands.describe(channel="Canal a ser limpo")
async def clear_houses(interaction: discord.Interaction, channel: discord.TextChannel):
    # Permissão: só administradores
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Você precisa ser administrador para usar este comando.", ephemeral=True)
        return

    await interaction.response.send_message(f"Limpando todas as mensagens do canal {channel.mention}...", ephemeral=True)

    deleted = 0
    try:
        def check(msg):
            return True  # Deleta tudo
        # Deleta em lotes de 100 (bulk delete só funciona para mensagens com até 14 dias)
        while True:
            msgs = [m async for m in channel.history(limit=100)]
            if not msgs:
                break
            await channel.delete_messages(msgs)
            deleted += len(msgs)
        # Para mensagens mais antigas, deleta uma a uma
        async for msg in channel.history(limit=None, oldest_first=True):
            try:
                await msg.delete()
                deleted += 1
            except Exception:
                pass
    except Exception as e:
        await interaction.followup.send(f"Erro ao deletar mensagens: {e}", ephemeral=True)
        return

    await interaction.followup.send(f"Foram deletadas {deleted} mensagens do canal {channel.mention}.", ephemeral=True)

@bot.tree.command(name="my_notifications", description="Gerencia suas notificações de casas")
async def my_notifications(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    if user_id not in user_notifications or not user_notifications[user_id]["notifications"]:
        await interaction.response.send_message("Você não tem nenhuma notificação ativa.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🔔 Suas Notificações",
        description="Lista de casas que você está monitorando:",
        color=discord.Color.blue()
    )
    
    for house_key in user_notifications[user_id]["notifications"]:
        world, district, ward, plot = house_key.split('_')
        embed.add_field(
            name=f"🏰 {district} - Ward {ward} Plot {plot}",
            value=f"🌍 {world.capitalize()}",
            inline=False
        )
    
    class NotificationManager(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)  # 5 minutos de timeout
        
        @discord.ui.button(label="Remover Todas", style=discord.ButtonStyle.danger)
        async def remove_all(self, interaction: discord.Interaction, button: discord.ui.Button):
            if str(interaction.user.id) != user_id:
                await interaction.response.send_message("Este botão não é para você!", ephemeral=True)
                return
            
            user_notifications[user_id]["notifications"] = []
            save_user_notifications()
            await interaction.response.send_message("Todas as suas notificações foram removidas.", ephemeral=True)
            await interaction.message.delete()
    
    await interaction.response.send_message(embed=embed, view=NotificationManager(), ephemeral=True)

# Inicia o bot
bot.run(os.getenv('DISCORD_TOKEN')) 