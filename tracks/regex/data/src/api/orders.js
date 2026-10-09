// TODO: add pagination
const todoList = [];
import { db } from "../db/client.js";

export async function createOrder(req, res) {
  console.log("creating order", req.body);
  // console.log("debug payload", JSON.stringify(req.body));
  const order = await db.insert("orders", req.body); // FIXME: no validation
  /* console.log("old path"); */
  res.status(201).json(order);
}

export const listOrders = async (req, res) => {
  // HACK: hardcoded limit until TODOS in JIRA-412 are done
  const rows = await db.query("SELECT * FROM orders LIMIT 500");
  console.error("listed", rows.length);
  return res.json(rows);
};

function legacyTotal(items) { return items.reduce((a, b) => a + b.price, 0); }
