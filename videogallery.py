from flask import Flask, url_for, request
from flask import render_template as template
from operator import itemgetter
app = Flask(__name__)
import os
import synq
import json


# get values from environment
synq_api_key = os.getenv('SYNQ_VIDEO_GALLERY_API_KEY')
debug = (os.getenv('SYNQ_VIDEO_GALLERY_DEBUG') is not None) or False 
port = os.getenv('PORT') or '5000'


videoAPI = synq.VideoAPI(synq_api_key)

sources = {
	"set_tags":"""
video.userdata.tags= {};
"""
}

queries = {
	"all": """
if(_.get(video,"player.thumbnail_url") != undefined){
	return {"created_at": video.created_at, "video_id" : video.video_id, "player" : video.player, "tags" : _.get(video,"userdata.tags")};
}
""",
	"by_tags" : """
includes_all = function (collection,elements){{
    ret_val = true;
	elements.forEach(function(v){{
        if(_.includes(collection,v) == false){{
			ret_val = false;
        }}
    }})
	return ret_val;
}}
if(_.get(video,"player.thumbnail_url") == undefined) return undefined;
if(_.get(video,"userdata.tags") == undefined) return undefined;
if(includes_all(_.get(video,"userdata.tags"),{})){{
	return {{"created_at": video.created_at, "video_id" : video.video_id, "player" : video.player, "tags" : _.get(video,"userdata.tags")}};
}}
""",
	"by_id": """
if(_.get(video,"player.thumbnail_url") != undefined){{
	if(video.video_id == "{}"){{
		return {{"video_id" : video.video_id, "player" : video.player, "tags" : _.get(video,"userdata.tags")}};
	}}
}}
"""
}

def tagstring_to_tags(tagstring):
	tags = tagstring.split(",")
	tags = [tag.strip() for tag in tags]
	tags = list(set(tags))
	if(tags.count("") != 0):
		tags.remove("")
	return tags

def tags_to_tagstring(tags):
	tags = [tag.strip() for tag in tags]
	tags = list(set(tags))
	if(tags.count("") != 0):
		tags.remove("")
	tagstring = ", ".join(sorted(tags))
	return tagstring

def set_tags(video_id,tag_list):
	if(debug):
		print("setting {} tags to {}".format(video_id,tag_list))
	return videoAPI.update(video_id,sources["set_tags"].format(tag_list))

def sort_videos(video_list):
	return sorted(video_list, key=itemgetter('created_at'), reverse=True)

def find_all():
	return videoAPI.query(queries["all"])

def find_by_tags(tag_list):
	return videoAPI.query(queries["by_tags"].format(tag_list))

def find_by_id(id):
	return videoAPI.query(queries["by_id"].format(id))

def num_uploaded():
	return len(find_all())

# Gallery front page
@app.route("/")
def index():
	url_for('static', filename='style.css')
	url_for('static', filename='app.js')
	return template('index.html', num_uploaded=num_uploaded())

# Video gallery browsing page
@app.route("/posts/")
def posts():
	url_for('static', filename='style.css')
	url_for('static', filename='app.js')
	tagstring = request.args.get("tags")
	videos = []
	if(tagstring is None or tagstring == ""):
		videos = find_all();
	else:
		tags = tagstring_to_tags(tagstring)
		videos = find_by_tags(tags)
		tagstring = tags_to_tagstring(tags)
	videos = sort_videos(videos)
	return template('posts.html', videos=videos, searchbox=tagstring)


# Page for uploading a new video
@app.route("/upload/")
def upload():
	video_id = videoAPI.create()["video_id"]
	uploader_url = videoAPI.uploader(video_id)["uploader_url"]
	return template('upload.html', video_id=video_id, uploader_url = uploader_url)


# Page for viewing a single video
@app.route("/post/")
def post():
	video_id = request.args.get("video")
	video = find_by_id(video_id)[0]
	tags = video.get("tags")
	if tags is None:
		return template('post.html', video=video)
	else:
		tagstring = tags_to_tagstring(tags)
		return template('post.html', video=video, tagstring=tagstring)

# http POST call to update tags.
# Called from upload and viewing page
@app.route("/tags/", methods=['POST'])
def tags():
	video_id = request.form["video_id"]
	tagstring = request.form["tags"]
	tags = tagstring_to_tags(tagstring)
	set_tags(video_id,tags)
	return json.dumps({'status':'OK'})

if __name__ == "__main__":
	app.run(port=port)