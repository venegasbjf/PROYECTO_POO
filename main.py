import webview



def load_url(window):
    window.load_url('./src/views/pre.html')


window = webview.create_window(title='GameDeck', width = 1280, height = 720, \
                      resizable = False, fullscreen = False, text_select = False, confirm_close = True)

webview.start(load_url, window)