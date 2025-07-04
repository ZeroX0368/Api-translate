from flask import Flask, request, jsonify
from googletrans import Translator, LANGUAGES

app = Flask(__name__)
translator = Translator()

# Google Translate language codes mapping
GOOGLE_TRANSLATE = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
    'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
    'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'zh': 'Chinese', 'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)', 'co': 'Corsican', 'hr': 'Croatian',
    'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
    'eo': 'Esperanto', 'et': 'Estonian', 'fi': 'Finnish', 'fr': 'French',
    'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian', 'de': 'German',
    'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa',
    'haw': 'Hawaiian', 'he': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong',
    'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian',
    'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese', 'jv': 'Javanese',
    'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'rw': 'Kinyarwanda',
    'ko': 'Korean', 'ku': 'Kurdish', 'ky': 'Kyrgyz', 'lo': 'Lao',
    'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish',
    'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam',
    'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian',
    'my': 'Myanmar', 'ne': 'Nepali', 'no': 'Norwegian', 'ny': 'Nyanja',
    'or': 'Odia', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish',
    'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian',
    'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho',
    'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak',
    'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese',
    'sw': 'Swahili', 'sv': 'Swedish', 'tl': 'Tagalog', 'tg': 'Tajik',
    'ta': 'Tamil', 'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai',
    'tr': 'Turkish', 'tk': 'Turkmen', 'uk': 'Ukrainian', 'ur': 'Urdu',
    'ug': 'Uyghur', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh',
    'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

def get_translation_result(input_text, output_code):
    """Get translation result"""

    if output_code not in GOOGLE_TRANSLATE:
        return {
            'error': 'Invalid translation code',
            'message': 'Visit https://cloud.google.com/translate/docs/languages for supported codes',
            'supported_languages': list(GOOGLE_TRANSLATE.keys())
        }

    if not input_text or input_text.strip() == '':
        return {'error': 'Please provide valid translation text'}

    try:
        # Create a fresh translator instance to avoid caching issues
        fresh_translator = Translator()
        result = fresh_translator.translate(input_text, dest=output_code)
        
        # Handle potential async/coroutine issues
        if hasattr(result, '__await__'):
            # If it's a coroutine, we need to handle it differently
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            result = loop.run_until_complete(result)

        return {
            'success': True,
            'original_text': input_text,
            'translated_text': result.text,
            'input_language': GOOGLE_TRANSLATE.get(result.src, result.src),
            'input_code': result.src,
            'output_language': GOOGLE_TRANSLATE.get(output_code, output_code),
            'output_code': output_code,
            'translation_info': f"{GOOGLE_TRANSLATE.get(result.src, result.src)} ({result.src}) → {GOOGLE_TRANSLATE.get(output_code, output_code)} ({output_code})"
        }

    except Exception as e:
        return {'error': f'Translation failed: {str(e)}'}

@app.route('/translate')
def translate_endpoint():
    """Main translation endpoint"""
    output_code = request.args.get('to', request.args.get('language', 'vi'))
    input_text = request.args.get('text', request.args.get('message', ''))

    result = get_translation_result(input_text, output_code)

    if 'error' in result:
        return jsonify(result), 400

    # Configure JSON to display Vietnamese characters properly
    response = app.response_class(
        response=app.json.dumps(result, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json; charset=utf-8'
    )
    return response

@app.route('/translate/<output_code>')
def translate_with_path(output_code):
    """Alternative endpoint with language code in path"""
    input_text = request.args.get('text', request.args.get('message', ''))

    result = get_translation_result(input_text, output_code)

    if 'error' in result:
        return jsonify(result), 400

    # Configure JSON to display Vietnamese characters properly
    response = app.response_class(
        response=app.json.dumps(result, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json; charset=utf-8'
    )
    return response

@app.route('/languages')
def get_languages():
    """Get all supported languages"""
    return jsonify({
        'supported_languages': GOOGLE_TRANSLATE,
        'total_count': len(GOOGLE_TRANSLATE)
    })

@app.route('/languages/<search>')
def search_languages(search):
    """Search for languages by name or code"""
    search = search.lower()
    results = {}

    for code, name in GOOGLE_TRANSLATE.items():
        if search in code.lower() or search in name.lower():
            results[code] = name

    return jsonify({
        'search_term': search,
        'results': results,
        'count': len(results)
    })

@app.route('/status')
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'features': [
            'Text translation',
            'Language detection',
            'Multiple endpoints',
            'Language search'
        ],
        'supported_languages_count': len(GOOGLE_TRANSLATE)
    })

@app.route('/')
def home():
    return '''
    <h1>🌐 Translation API Service</h1>
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">

        <h2>📚 API Endpoints</h2>

        <h3>🔤 Translate Text</h3>
        <p><strong>GET</strong> <code>/translate?to=vi&text=hello</code></p>
        <p><strong>GET</strong> <code>/translate/vi?text=hello</code></p>
        <p>Aliases: <code>language</code> for <code>to</code>, <code>message</code> for <code>text</code></p>

        <h3>🌍 Get Languages</h3>
        <p><strong>GET</strong> <a href="/languages">/languages</a> - All supported languages</p>
        <p><strong>GET</strong> <a href="/languages/spanish">/languages/spanish</a> - Search languages</p>

        <h3>📊 API Status</h3>
        <p><strong>GET</strong> <a href="/status">/status</a> - API information</p>

        <h2>🚀 Examples</h2>
        <ul>
            <li><a href="/translate?to=vi&text=hello">/translate?to=vi&text=hello</a> (Vietnamese)</li>
            <li><a href="/translate?to=es&text=good morning">/translate?to=es&text=good morning</a> (Spanish)</li>
            <li><a href="/translate/fr?text=thank you">/translate/fr?text=thank you</a> (French)</li>
            <li><a href="/translate?to=ja&text=how are you">/translate?to=ja&text=how are you</a> (Japanese)</li>
        </ul>

        <h2>⚡ Features</h2>
        <ul>
            <li>✅ 100+ supported languages</li>
            <li>✅ Automatic language detection</li>
            <li>✅ Multiple endpoint formats</li>
            <li>✅ Language search functionality</li>
            <li>✅ Detailed error messages</li>
        </ul>

        <h2>🔧 Parameters</h2>
        <ul>
            <li><code>to</code> or <code>language</code>: Target language code (e.g., 'vi', 'es', 'fr')</li>
            <li><code>text</code> or <code>message</code>: Text to translate</li>
        </ul>

        <p>📋 <a href="/languages">View all supported language codes</a></p>
    </div>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
