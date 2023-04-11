const order = { client: "Амир", number: "228", date: "13.04.2023" };

const info = [
  {
    price: 100,
    type: "Почини",
    status: "Выполнен",
  },
  {
    price: 200,
    type: "Чиню",
    status: "Выполняется",
  },
];

const mainBox = document.createElement("div");
mainBox.className = "mainBox";

const orderHead = document.createElement("div");
orderHead.className = "orderHead";

const orderNumber = document.createElement("label");
orderNumber.className = "orderNumber";
orderNumber.textContent = "Ваш заказ: " + order.number;

const clientName = document.createElement("label");
clientName.className = "clientName";
clientName.textContent = "ФИО: " + order.client;

const orderPage = document.createElement("div");
orderPage.className = "orderPage";

orderHead.append(orderNumber, clientName);

info.map((order) => {
  const orderInfo = document.createElement("div");
  orderInfo.className = "orderInfo";

  const orderType = document.createElement("label");
  orderType.className = "orderType";
  orderType.textContent = order.type;

  const orderStatus = document.createElement("label");
  orderStatus.className = "orderStatus";
  orderStatus.textContent = order.status;

  const orderPrice = document.createElement("label");
  orderPrice.className = "orderPrice";
  orderPrice.textContent = "Цена: " + order.price;

  orderPage.append(orderInfo);
  orderInfo.append(orderType, orderStatus, orderPrice);
});

const orderSum = document.createElement("div");
orderSum.className = "orderSum";

const totalPrice = info.reduce((accum, item) => accum + item.price, 0);

const orderSummaryPrice = document.createElement("label");
orderSummaryPrice.className = "orderSummaryPrice";
orderSummaryPrice.textContent = "Итого: " + totalPrice;

const orderDate = document.createElement("label");
orderDate.className = "orderDate";
orderDate.textContent = "Будет готов к " + order.date;

orderSum.append(orderSummaryPrice, orderDate);
orderPage.append(orderSum);
mainBox.append(orderHead, orderPage);
document.body.append(mainBox);
