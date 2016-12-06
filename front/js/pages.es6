{
  const DOM = {
    $galleryTarget: $('.news-wrapper .gbi-photo'),
    $mapPoint: $('.js-map-point'),
  };

  const points = [
    [59.89161, 30.40879],   // СПб, головной
    [59.793747, 30.648533], // СПб, производство
    [55.78895, 37.70772],   // Москва
    [64.538237, 40.520236], // Архангельск
    [68.95294, 33.080883],  // Мурманск
    [55.780897, 49.1273],   // Казань
    [56.774342, 60.6135],   // Екатеринбург
    [66.535145, 66.606638], // Салехард
  ];

  const mapPoints = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        id: 0,
        geometry: { type: 'Point', coordinates: points[0] },
        properties: {
          balloonContent: '<p>192148, Санкт-Петербург, головной офис, пр. Елизарова, 38А, офис 218</p>' +
                          '<p>8 (812) 648-13-80, 8 (812) 642-47-09</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Санкт-Петербург, головной офис',
        },
      },
      {
        type: 'Feature',
        id: 1,
        geometry: { type: 'Point', coordinates: points[1] },
        properties: {
          balloonContent: '<p>188683, Санкт-Петербург, производство, пос.им.Свердлова, промышленная зона, улица' +
                          ' Овцынская</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Санкт-Петербург, производство',
        },
      },
      {
        type: 'Feature',
        id: 2,
        geometry: { type: 'Point', coordinates: points[2] },
        properties: {
          balloonContent: '<p>107023, Москва, улица Электрозаводская, 24</p>' +
                          '<p>8(499) 322-31-98</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Москва',
        },
      },
      {
        type: 'Feature',
        id: 3,
        geometry: { type: 'Point', coordinates: points[3] },
        properties: {
          balloonContent: '<p>163100, Архангельск, площадь Ленина, д. 3</p>' +
                          '<p>8 (8182) 63-92-35</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Архангельск',
        },
      },
      {
        type: 'Feature',
        id: 4,
        geometry: { type: 'Point', coordinates: points[4] },
        properties: {
          balloonContent: '<p>Мурманск, проспект Ленина, д. 16А</p>' +
                          '<p>8 (8152) 65-50-48</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Мурманск',
        },
      },
      {
        type: 'Feature',
        id: 5,
        geometry: { type: 'Point', coordinates: points[5] },
        properties: {
          balloonContent: '<p>Казань, Республика Татарстан, Спартаковская улица, 2</p>' +
                          '<p>8 (343) 318-26-91</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Казань',
        },
      },
      {
        type: 'Feature',
        id: 6,
        geometry: { type: 'Point', coordinates: points[6] },
        properties: {
          balloonContent: '<p>Екатеринбург, Свердловская область, улица Титова, 27, литер. З</p>' +
                          '<p>8 (343) 318-26-91</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Екатеринбург',
        },
      },
      {
        type: 'Feature',
        id: 7,
        geometry: { type: 'Point', coordinates: points[7] },
        properties: {
          balloonContent: '<p>629007, Ямало-Ненецкий автономный округ, Салехард, улица Чубынина, 34</p>' +
                          '<p>8 (34922) 99-35-8</p><p>ПН-ПТ с 9.00 до 18.00</p>',
          hintContent: 'Салехард',
        },
      },
    ],
  };

  const init = () => {
    pluginsInit();
  };

  /**
   * https://goo.gl/Lw1RG9 - Featherlight Gallery
   * https://tech.yandex.ru/maps/ - Yandex Maps
   */
  function pluginsInit() {
    DOM.$galleryTarget.featherlightGallery();
    ymaps.ready(initMap);
  }

  function initMap() {
    const myMap = new ymaps.Map('map', {
      center: [64, 48],
      zoom: 3,
      controls: ['smallMapDefaultSet'],
    });

    const objectManager = new ymaps.ObjectManager({
      clusterize: true,
      gridSize: 32,
    });

    objectManager.objects.options.set('preset', 'islands#redDotIcon');
    objectManager.clusters.options.set('preset', 'islands#redClusterIcons');
    myMap.geoObjects.add(objectManager);

    objectManager.add(mapPoints);

    // Set map center on click on text sections:
    DOM.$mapPoint.click(function() {
      const city = $(this).data('id');

      DOM.$mapPoint.removeClass('active');
      $(this).addClass('active');

      myMap.setCenter(points[city], 16)
        .then(() => {
          setTimeout(() => {
            objectManager.objects.balloon.open(city);
          }, 800);
        }, (err) => {
          console.error(err);
        });
    });
  }

  init();
}
