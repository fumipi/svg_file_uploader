import base64
import requests
import streamlit as st
import webbrowser

# SVG画像を保存するGithubレポジトリ情報
username = 'fumipi'
repo_name = 'svg_files'
access_token = st.secrets["github_access_token"]

def store_svg_to_github(svg_content, commit_message):
    # SVGをbase64へエンコード
    svg_content_base64 = base64.b64encode(svg_content).decode('utf-8')
    
    # Github APIに渡すURL
    url = f'https://api.github.com/repos/{username}/{repo_name}/contents/uploaded.svg'
    
    # 送信内容
    payload = {
        'message': commit_message,
        'content': svg_content_base64
    }
    
    # もしファイルがすでに存在している場合はshaを取得して更新する
    response = requests.get(url, headers={
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    })
    
    if response.status_code == 200:
        # ファイルが存在するので更新する
        sha = response.json()['sha']
        payload['sha'] = sha
        response = requests.put(url, json=payload, headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        })
    else:
        # ファイルが存在していないので、ファイルを作成する
        response = requests.put(url, json=payload, headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        })
    
    return response

def main():
    st.title('SVG Uploader')
    st.text('自走式ペンプロッタープリンターが描く画像をアップロードするアプリです。 \n画像がアップロードできたらロボットを動かすシミュレーションを開始します。')
    
    # ファイルアップロードUI
    uploaded_file = st.file_uploader('SVG画像を選択', type=['svg'])
    
    if uploaded_file is not None:
        # アップロードされたファイルを読み込む
        svg_content = uploaded_file.read()
        
        # コミットメッセージ入力
        commit_message = st.text_input('Commit message', value='Add or update SVG file')
        
        # SVGファイルをGithubに登録
        if st.button('SVGファイルを登録してシミュレーションをスタート'):
            response = store_svg_to_github(svg_content, commit_message)
            
            if response.status_code in [200, 201]:
             
                # ユーザーのデフォルトブラウザーでwebots.cloudのシミュレーションを開く
                simulation_url = "https://webots.cloud/run?version=R2023b&url=https%3A%2F%2Fgithub.com%2Ffumipi%2Fautonomous_pen_plotter_concept%2Fblob%2Fmain%2Fworlds%2Fpenbot.wbt&type=demo"
                webbrowser.open(simulation_url, new = 1)
                
                st.markdown(f'SVGファイルが登録できました。シミュレーションは、ユーザーのデフォルトブラウザーで開いています。もし開いていない場合は[ここ]({simulation_url})をクリックしてください。', unsafe_allow_html=True)
            else:
                st.error(f'Failed to store the SVG file. Status code: {response.status_code}')
                st.error(f'Error message: {response.text}')

if __name__ == '__main__':
    main()