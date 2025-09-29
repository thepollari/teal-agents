package telemetry

import (
	"os"

	"github.com/sirupsen/logrus"
)

type LogLevel string

const (
	DebugLevel LogLevel = "debug"
	InfoLevel  LogLevel = "info"
	WarnLevel  LogLevel = "warn"
	ErrorLevel LogLevel = "error"
	FatalLevel LogLevel = "fatal"
)

type LoggerConfig struct {
	Level  LogLevel `yaml:"level" json:"level"`
	Format string   `yaml:"format" json:"format"` // "json" or "text"
	Output string   `yaml:"output" json:"output"` // "stdout", "stderr", or file path
}

func NewLogger(config LoggerConfig) *logrus.Logger {
	logger := logrus.New()

	switch config.Level {
	case DebugLevel:
		logger.SetLevel(logrus.DebugLevel)
	case InfoLevel:
		logger.SetLevel(logrus.InfoLevel)
	case WarnLevel:
		logger.SetLevel(logrus.WarnLevel)
	case ErrorLevel:
		logger.SetLevel(logrus.ErrorLevel)
	case FatalLevel:
		logger.SetLevel(logrus.FatalLevel)
	default:
		logger.SetLevel(logrus.InfoLevel)
	}

	if config.Format == "json" {
		logger.SetFormatter(&logrus.JSONFormatter{
			TimestampFormat: "2006-01-02T15:04:05.000Z07:00",
		})
	} else {
		logger.SetFormatter(&logrus.TextFormatter{
			FullTimestamp:   true,
			TimestampFormat: "2006-01-02T15:04:05.000Z07:00",
		})
	}

	switch config.Output {
	case "stderr":
		logger.SetOutput(os.Stderr)
	case "stdout":
		logger.SetOutput(os.Stdout)
	default:
		if config.Output != "" {
			if file, err := os.OpenFile(config.Output, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666); err == nil {
				logger.SetOutput(file)
			} else {
				logger.SetOutput(os.Stdout)
				logger.Warnf("Failed to open log file %s, using stdout: %v", config.Output, err)
			}
		} else {
			logger.SetOutput(os.Stdout)
		}
	}

	return logger
}

func GetDefaultLogger() *logrus.Logger {
	return NewLogger(LoggerConfig{
		Level:  InfoLevel,
		Format: "text",
		Output: "stdout",
	})
}

func WithFields(logger *logrus.Logger, fields map[string]interface{}) *logrus.Entry {
	return logger.WithFields(logrus.Fields(fields))
}
