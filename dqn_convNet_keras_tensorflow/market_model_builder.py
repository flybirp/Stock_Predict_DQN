class MarketDeepQLearningModelBuilder():
    def buildModel(self):
        from keras.models import Model
        from keras.layers import merge, Conv2D, MaxPooling2D, Input, Dense, Flatten, Dropout, Reshape, TimeDistributed, BatchNormalization, Merge, merge
        from keras.layers.merge import concatenate
        from keras.layers.advanced_activations import LeakyReLU

        merges = []
        inputs = []

        """B0"""
        B0 = Input(shape=(2, ))
        b = Dense(5, activation="sigmoid")(B0)

        inputs.append(B0)
        merges.append(b)

        """S0"""
        S0 = Input(shape=(7, 60, 1, ))

        # s = Flatten()(S0)
        s = Conv2D(filters=2048, kernel_size=(1, 60), strides=1, padding='valid', data_format='channels_last')(S0)
        s = LeakyReLU(0.001)(s)
        s = Flatten()(s)
        s = Dense(512)(s)
        s = LeakyReLU(0.001)(s)

        inputs.append(S0)
        merges.append(s)


        m = concatenate(merges, axis=1)
        m = Dense(1024)(m)
        m = LeakyReLU(0.001)(m)
        m = Dense(512)(m)
        m = LeakyReLU(0.001)(m)
        m = Dense(256)(m)
        m = LeakyReLU(0.001)(m)
        V = Dense(3, activation='linear')(m)

        model = Model(inputs=inputs, outputs=V)

        print model.summary()

        return model


