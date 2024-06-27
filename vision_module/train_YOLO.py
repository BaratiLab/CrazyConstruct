from ultralytics import YOLO

def main():
    model = YOLO('yolov8n.pt')
    results = model.train(data="data/data.yaml", epochs=15, imgsz=640, optimizer="Adam",lr0=1e-3)


if __name__ == '__main__':
    main()