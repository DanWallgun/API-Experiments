package main

import (
	"context"
	"fmt"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"
	"gocv.io/x/gocv"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

const (
	BotToken   = "968239867:AAGAY5gAqPIHSz850ljCyDlrgnJLShZUsbo"
	WebhookURL = "https://telegram-image-bot.herokuapp.com/"
)

func handleStatus(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("All is working?"))
}

type CVHelper struct {
	CurrentImage gocv.Mat
}

func (cv *CVHelper) InitFromBytes(inputBytes []byte) error {
	var err error
	cv.CurrentImage, err = gocv.IMDecode(inputBytes, gocv.IMReadUnchanged)
	if err != nil {
		return err
	}
	return nil
}

func (cv *CVHelper) GetJPEGBytes() ([]byte, error) {
	return gocv.IMEncode(gocv.JPEGFileExt, cv.CurrentImage)
}

func (cv *CVHelper) Canny(t1, t2 float32) {
	edges := gocv.NewMat()
	gocv.Canny(cv.CurrentImage, &edges, t1, t2)
	cv.CurrentImage = edges
}

func handleCanny(bot *tgbotapi.BotAPI, message *tgbotapi.Message) error {
	photoSize := (*message.Photo)[len(*message.Photo)-1]

	url, err := bot.GetFileDirectURL(photoSize.FileID)
	if err != nil {
		return err
	}
	resp, err := http.Get(url)
	if err != nil {
		return err
	}

	imageBytes := tgbotapi.FileBytes{
		Bytes: nil,
	}
	imageBytes.Bytes, err = ioutil.ReadAll(resp.Body)
	resp.Body.Close()
	if err != nil {
		return err
	}

	cv := &CVHelper{}
	err = cv.InitFromBytes(imageBytes.Bytes)
	if err != nil {
		return err
	}
	cv.Canny(20, 220)
	imageBytes.Bytes, err = cv.GetJPEGBytes()
	if err != nil {
		return err
	}

	photoMsg := tgbotapi.NewPhotoUpload(message.Chat.ID, imageBytes)

	_, err = bot.Send(photoMsg)
	if err != nil {
		return err
	}

	return nil
}

func handleUpdates(bot *tgbotapi.BotAPI) {
	updates := bot.ListenForWebhook("/")

	const (
		INLINE_CANNY        string = "inlineData_canny"
		INLINE_CUSTOMPIXELS string = "inlineData_customPixels"
	)

	currentChatImage := make(map[int64]gocv.Mat)

	for update := range updates {
		if update.Message != nil && update.Message.Photo != nil {
			inlineMarkup := tgbotapi.NewInlineKeyboardMarkup(
				tgbotapi.NewInlineKeyboardRow(
					tgbotapi.NewInlineKeyboardButtonData("Canny", INLINE_CANNY),
				),
				tgbotapi.NewInlineKeyboardRow(
					tgbotapi.NewInlineKeyboardButtonData("Custom Pixels", INLINE_CUSTOMPIXELS),
				),
			)
			msg, err := bot.Send(tgbotapi.NewMessage(update.Message.Chat.ID, "Test Message"))
			msg, err = bot.Send(tgbotapi.NewEditMessageReplyMarkup(update.Message.Chat.ID, msg.MessageID, inlineMarkup))

			//err := handleImage(bot, update.Message)
			photoSize := (*update.Message.Photo)[len(*update.Message.Photo)-1]
			url, err := bot.GetFileDirectURL(photoSize.FileID)
			if err != nil {
				log.Printf("ErrorGetFileURL\n%s", err.Error())
				continue
			}
			resp, err := http.Get(url)
			if err != nil {
				log.Printf("ErrorHttpGet\n%s", err.Error())
				continue
			}

			imageBytes, err := ioutil.ReadAll(resp.Body)
			resp.Body.Close()
			if err != nil {
				log.Printf("ErrorInline\n%s", err.Error())
				continue
			}

			currentChatImage[update.Message.Chat.ID], err = gocv.IMDecode(imageBytes, gocv.IMReadUnchanged)
			if err != nil {
				log.Printf("ErrorInline\n%s", err.Error())
				continue
			}
		}
		if update.CallbackQuery != nil {
			_, err := bot.AnswerCallbackQuery(tgbotapi.NewCallback(update.CallbackQuery.ID, ""))
			if err != nil {
				log.Printf("AnswerCallbackQuery Error.\n%s", err.Error())
				continue
			}
			if update.CallbackQuery.Data == INLINE_CANNY {
				edges := gocv.NewMat()
				gocv.Canny(currentChatImage[update.CallbackQuery.Message.Chat.ID], &edges, 16, 240)
				currentChatImage[update.CallbackQuery.Message.Chat.ID] = edges

				imageBytes, err := gocv.IMEncode(gocv.JPEGFileExt, currentChatImage[update.CallbackQuery.Message.Chat.ID])
				if err != nil {
					log.Printf("Encode Error.\n%s", err.Error())
					continue
				}

				photoMsg := tgbotapi.NewPhotoUpload(
					update.CallbackQuery.Message.Chat.ID,
					tgbotapi.FileBytes{
						Bytes: imageBytes,
					},
				)
				_, err = bot.Send(photoMsg)
				if err != nil {
					log.Printf("SendPhoto Error.\n%s", err.Error())
					continue
				}
			}
		}
	}
}

func startTaskBot(ctx context.Context) error {
	bot, err := tgbotapi.NewBotAPI(BotToken)
	if err != nil {
		log.Fatalf("NewBotAPI failed: %s", err)
		return err
	}

	bot.Debug = true
	fmt.Printf("Authorized on account %s\n", bot.Self.UserName)

	_, err = bot.SetWebhook(tgbotapi.NewWebhook(WebhookURL))
	if err != nil {
		log.Fatalf("SetWebhook failed: %s", err)
		return err
	}

	http.HandleFunc("/status", handleStatus)

	port := os.Getenv("PORT")
	go func() {
		log.Fatalln("http err:", http.ListenAndServe(":"+port, nil))
	}()
	fmt.Println("start listen :8080")

	log.Printf("Time to handle updates:")
	// there is no context processing just because it is context.Background()
	handleUpdates(bot)

	return nil
}

func main() {
	err := startTaskBot(context.Background())
	if err != nil {
		panic(err)
	}
}
