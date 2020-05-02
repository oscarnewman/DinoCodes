//
//  AVScanner.swift
//  QRCapture
//
//  Created by Oscar Newman on 4/30/20.
//  Copyright © 2020 Oscar Newman. All rights reserved.
//

import Foundation
import AVFoundation
import Combine
import UIKit
import SwiftUI

class CaptureViewController: UIViewController
{
    
    var captureSession: AVCaptureSession!
    var stillImageOutput: AVCapturePhotoOutput!
    var videoPreviewLayer: AVCaptureVideoPreviewLayer!
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        
        captureSession = AVCaptureSession()
        captureSession.sessionPreset = .medium
        
        guard let backCamera = AVCaptureDevice.default(for: AVMediaType.video)
            else {
                print("Unable to access back camera!")
                return
        }
        
        do {
            let input = try AVCaptureDeviceInput(device: backCamera)
            //Step 9
            if captureSession.canAddInput(input) && captureSession.canAddOutput(stillImageOutput) {
                captureSession.addInput(input)
//                captureSession.addOutput(stillImageOutput)
                setupLivePreview()
            }
        }
        catch let error  {
            print("Error Unable to initialize back camera:  \(error.localizedDescription)")
        }
        
        
    }
    
    func setupLivePreview() {
        
        videoPreviewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        
        videoPreviewLayer.videoGravity = .resizeAspect
        videoPreviewLayer.connection?.videoOrientation = .portrait
        self.view.layer.addSublayer(videoPreviewLayer)
        
        //Step12
        
        DispatchQueue.global(qos: .userInitiated).async {
            self.captureSession.startRunning()
            //Step 13
            
            DispatchQueue.main.async {
                self.videoPreviewLayer.frame = self.view.frame
            }
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        self.captureSession.stopRunning()
    }
}


struct CaptureView: UIViewControllerRepresentable {
    typealias UIViewControllerType = CaptureViewController

    func makeUIViewController(context: Context) -> CaptureViewController {
        return CaptureViewController()
    }
    
    func updateUIViewController(_ uiViewController: CaptureViewController, context: Context) {
        // do nothing
    }
    
}
