import 'package:flutter/material.dart';
import 'package:tflite/tflite.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/cupertino.dart';
import 'dart:html';
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_downloader/image_downloader.dart';
import 'dart:typed_data';
import 'dart:ui' as ui;

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(title: 'SpokesSimpsons'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Widget _image;
  bool _loading = false;
  Image inputImage = Image.network(
    'https://life.qizy.tech/wp-content/uploads/2020/01/2560.jpg',
  );
  final myController = TextEditingController();

  Widget inProcessIndicator() => Center(
          child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Text('加载中...', style: TextStyle(color: Colors.grey)),
          Text('(此过程可能消化30~60s)', style: TextStyle(color: Colors.grey)),
          CupertinoActivityIndicator()
        ],
      ));

  Widget _loadingCover() => Positioned(
        child: _loading
            ? Container(
                child: inProcessIndicator(),
                color: Colors.white.withOpacity(0.8),
              )
            : Container(),
      );

  @override
  void dispose() {
    myController.dispose();
    Tflite.close();
    super.dispose();
  }

  void _getFile() async {
    final completer = Completer<String>();
    final InputElement input = document.createElement('input');
    input
      ..type = 'file'
      ..accept = 'image/*';
    input.onChange.listen((e) async {
      final List<File> files = input.files;
      final reader = new FileReader();
      reader.readAsDataUrl(files[0]);
      reader.onError.listen((error) => completer.completeError(error));
      await reader.onLoad.first;
      completer.complete(reader.result as String);
    });
    input.click();

    final base64String = await completer.future;

    setState(() {
      inputImage = Image.memory(base64Decode(base64String.split(',')[1]));
    });

    _img2text(base64String.split(',')[1]);
  }

  void _img2text(String imageData) async {
    setState(() {
      _loading = true;
    });
    var response = await http.post('https://sim-backend.qizy.tech/img2text',
        body: imageData);
    String body = jsonDecode(response.body)['data'];

    setState(() {
      _loading = false;
      myController.text = body;
    });

    _text2img(body);
  }

  void _text2img(String text) async {
    setState(() {
      _loading = true;
    });
    var response =
        await http.post('https://sim-backend.qizy.tech/text2img', body: text);
    final body = jsonDecode(response.body)['data'];
    _image = Column(
      children: <Widget>[
        for (var item in body) Image.memory(base64Decode(item['py/b64']))
      ],
    );

    setState(() {
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: NetworkImage(
                'https://oi.qizy.tech/wp-content/uploads/2020/01/background.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: Center(
          child: Stack(children: <Widget>[
            Container(
              color: Colors.white.withOpacity(0.7),
            ),
            ListView(
              shrinkWrap: true,
              padding: const EdgeInsets.all(20),
              children: <Widget>[
                Text(
                  'If you looks like a Simpson, swims like a Simpson, and quacks like a Simpson, then you probably are a Simpson.',
                  textAlign: TextAlign.center,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                Container(height: 200, child: inputImage),
                RaisedButton(
                  textColor: Colors.white,
                  color: Colors.blueAccent,
                  onPressed: _getFile,
                  child: Text('Upload your WeChat Screenshot.',
                      style: TextStyle(fontSize: 20)),
                  shape: RoundedRectangleBorder(
                    borderRadius: new BorderRadius.circular(18.0),
                  ),
                ),
                Container(
                  padding: EdgeInsets.all(5),
                    decoration: new BoxDecoration(
                        borderRadius:
                            new BorderRadius.all(new Radius.circular(18.0)),
                        color: Colors.grey.withOpacity(0.9)),
                    child: TextField(
                      style: TextStyle(color: Colors.white),
                      controller: myController,
                      decoration: InputDecoration(
                        border: InputBorder.none,
                        hintStyle: TextStyle(color: Colors.white),
                        hintText: 'Enter your feeling...',
                      ),
                    )),
                RaisedButton(
                  color: Colors.blueAccent,
                  onPressed: () {
                    _text2img(myController.text);
                  },
                  textColor: Colors.white,
                  padding: const EdgeInsets.all(0.0),
                  child: Text('What does a Simpson say?',
                      style: TextStyle(fontSize: 20)),
                  shape: RoundedRectangleBorder(
                    borderRadius: new BorderRadius.circular(18.0),
                  ),
                ),
                if (_image != null) _image,
              ],
            ),
            _loadingCover(),
          ]),
        ),
      ),
    );
  }
}
