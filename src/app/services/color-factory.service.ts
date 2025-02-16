import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class ColorFactoryService {
    schemes;
    constructor() {
        this.schemes = this.getColorSchemes();
    }

    public getColor(name: string, index: number) {
        const scheme = this.schemes.find(s => s.name === name);
        if (scheme == null) {
            return { backgroundcolor: 'black', color: 'white', name: 'default', inactive: '', inactiveText: '', mouseover: '' };
        }
        const numCol = scheme.colors.length;
        const safeCol = index % numCol;
        return scheme.colors[safeCol];
    }
    public getScheme(name: string) {
        const scheme = this.schemes.find(s => s.name === name);
        if (scheme == null) {
            return [];
        } else return scheme;
    }
    public getSchemeByIndex(index: number): ColorScheme {
        return this.schemes[index % this.schemes.length];
    }
    // Inactive and InactiveText is set below the definitions where SetInactiveColorAndText is called
    private getColorSchemes(): ColorScheme[] {
        const pastelDarkText = '#444',
            schemes = [
                {
                    name: 'contrast',
                    colors: [
                        { backgroundcolor: '#e6194b', color: 'white', name: 'red', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#3cb44b', color: 'white', name: 'green', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ffe119', color: 'black', name: 'yellow', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#0082c8', color: 'white', name: 'blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#f58231', color: 'white', name: 'orange', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#911eb4', color: 'white', name: 'purple', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#46f0f0', color: 'black', name: 'cyan', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#f032e6', color: 'white', name: 'magenta', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#d2f53c', color: 'black', name: 'lime', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#fabebe', color: 'white', name: 'pink', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#008080', color: 'white', name: 'teal', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#e6beff', color: 'white', name: 'lavendar', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#aa6e28', color: 'white', name: 'brown', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#fffac8', color: 'white', name: 'beige', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#800000', color: 'white', name: 'maroon', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#aaffc3', color: 'white', name: 'mint', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#808000', color: 'white', name: 'olive', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#000080', color: 'white', name: 'navy', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ffd8b1', color: 'white', name: 'coral', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#808080', color: 'white', name: 'grey', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FFFFFF', color: 'white', name: 'white', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#000000', color: 'white', name: 'black', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'pastel',
                    colors: [
                        { backgroundcolor: '#F8A185', color: pastelDarkText, name: 'water melon', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FDF5A4', color: 'white', name: 'lemon chello', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FEC983', color: 'white', name: 'peaches and cream', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FBC1B3', color: 'white', name: 'coral reef', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#EFC0C8', color: 'white', name: 'musk mist', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#F7BDCB', color: 'white', name: 'comos field', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FBE4EE', color: pastelDarkText, name: 'marsh mallow', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#E9D1E1', color: 'white', name: 'dusty pink', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#E9D1E1', color: 'black', name: 'lilac lace', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FFF9FF', color: 'white', name: 'african violet', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ABC3E5', color: 'white', name: 'frosty lake', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#BDD2CB', color: 'white', name: 'storm clouds', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#C6D7E1', color: 'white', name: 'duck egg', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#BFDFF6', color: 'white', name: 'baby blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D9F1FD', color: pastelDarkText, name: 'powder blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#BCE2D7', color: 'white', name: 'spearmint', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#A2D5C6', color: 'white', name: 'teal breeze', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#82C99D', color: 'white', name: 'jade green', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#C7E4CE', color: 'white', name: 'african sage', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D4E5A1', color: 'white', name: 'wasabi ball', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#CAE5BC', color: 'white', name: 'mint tea', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D8EBCF', color: pastelDarkText, name: 'pistachio scoop', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#F3F5E7', color: pastelDarkText, name: 'vanilla canvas', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#CEC0A3', color: 'white', name: 'cafe latte', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'beach',
                    colors: [
                        { backgroundcolor: '#C0362C', color: 'white', name: 'red', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FF8642', color: 'white', name: 'orange', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#F4DC85', color: pastelDarkText, name: 'sand', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#816C5B', color: 'white', name: 'dirt', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#C3B7AC', color: 'white', name: 'stone', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#E7E3D7', color: pastelDarkText, name: 'light shade', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#668D3C', color: 'white', name: 'lush grass', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#B1DDA1', color: pastelDarkText, name: 'golf green', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#E5F3CF', color: pastelDarkText, name: 'grass sun', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#0097AC', color: 'white', name: 'medium blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#3CD6E6', color: 'white', name: 'tropic blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#97EAF4', color: pastelDarkText, name: 'shallow blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#007996', color: 'white', name: 'deep blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#06C2F4', color: 'white', name: 'cool blue', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#FAD8FA', color: pastelDarkText, name: 'chipper blue', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'neutral',
                    colors: [
                        { backgroundcolor: '#B7A6AD', color: 'white', name: 'neutral1', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#C8CAC0', color: 'white', name: 'neutral2', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D3C9CE', color: pastelDarkText, name: 'neutral3', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#BEB27A', color: 'white', name: 'neutral4', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D1C6BF', color: 'white', name: 'neutral5', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#DBD7CC', color: pastelDarkText, name: 'neutral6', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#CAB388', color: 'white', name: 'neutral7', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D5C4A1', color: pastelDarkText, name: 'neutral8', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#E0D48B', color: pastelDarkText, name: 'neutral9', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#B5B202', color: 'white', name: 'neutral10', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#C8C5AC', color: 'white', name: 'neutral11', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D5D3BF', color: pastelDarkText, name: 'neutral12', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#A8ADB4', color: 'white', name: 'neutral13', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#C3C8CD', color: 'white', name: 'neutral14', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D2D6D9', color: pastelDarkText, name: 'neutral15', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'earth',
                    colors: [
                        { backgroundcolor: '#493829', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#816C5B', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#A9A18C', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#612218', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#855723', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#B99C6B', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#8F3B1B', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#D57500', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#DBCA69', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#404F24', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#668D3C', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#BDD09F', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#4E6172', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#83929F', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#A3ADB8', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'beigetone',
                    colors: [
                        { backgroundcolor: '#b06660', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#d9a88f', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#eac3b8', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ca8f42', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#dbad72', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#f9d3a5', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ab9c73', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#d2be96', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#e3dcc0', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#5e7703', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#9baf8e', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#c1cc99', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#6a7d8e', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#aebbc7', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#c1d2d6', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'warm',
                    colors: [
                        { backgroundcolor: '#793f0d', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ac793d', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#c38e63', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#e49969', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#e5ae96', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#eec5a9', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#6e7649', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#9d9754', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#c7c937', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#b4a851', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#dfd27c', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#e7e3B5', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#846d74', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#b7a6ad', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#d3c9ce', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'cool',
                    colors: [
                        { backgroundcolor: '#004259', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#65a8c4', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#aacee2', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#8c65d3', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#9a93ec', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#cab9f1', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#0052a5', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#413bf7', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#81cbf8', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#00adce', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#59dbf1', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#9ee7fa', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#00c590', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#73ebae', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#b5f9d3', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'common',
                    colors: [
                        { backgroundcolor: '#002685', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#449adf', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#4dc7fd', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#4cde77', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#5e53c7', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#7e77d2', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#fc007f', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#fe79d1', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#763931', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#f1ab00', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#fadf00', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#fadf00', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#000000', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#007e3a', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#64d13e', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'basic',
                    colors: [
                        { backgroundcolor: '#b21f35', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#d82735', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ff7435', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ffa135', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#ffc835', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#fff735', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#00753a', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#009e47', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#16dd36', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#0052a5', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#0079e7', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#06a9fc', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#681e7e', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#7d3cb5', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#bd7af6', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'brooding',
                    colors: [
                        { backgroundcolor: '#502812', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#603618', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#855723', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#892034', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#7a1a57', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#6f256c', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#00344d', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#003066', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#575273', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#004236', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#404616', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#9f9b74', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#212930', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#868f98', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#C3C8CD', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
                {
                    name: 'graytone',
                    colors: [
                        { backgroundcolor: '#C88691', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#AD85ba', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#95a1c3', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#74a18e', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#818fb8', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#b2c891', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#b99c6b', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#e49960', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#c9c27f', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#949494', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#b2b2b2', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#d6d6d6', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#91867e', color: 'white', name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#b2aaa4', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                        { backgroundcolor: '#d9d5d2', color: pastelDarkText, name: '', inactive: '', inactiveText: '', mouseover: '' },
                    ],
                },
            ];
        return schemes;
    }
}

export interface ColorScheme {
    name: string;
    colors: ColorItem[];
}
export interface ColorItem {
    backgroundcolor: string;
    color: string;
    name: string;
    inactive: string;
    inactiveText: string;
    mouseover: string;
}
