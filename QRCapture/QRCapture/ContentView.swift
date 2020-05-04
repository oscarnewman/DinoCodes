//
//  ContentView.swift
//  QRCapture
//
//  Created by Oscar Newman on 4/30/20.
//  Copyright © 2020 Oscar Newman. All rights reserved.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        CameraViewController()
            .edgesIgnoringSafeArea(.top)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
